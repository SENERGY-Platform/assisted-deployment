"""
   Copyright 2020 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


from .configuration import config, user_dir
from .logger import getLogger
from .browser import Browser
from .workload import WorkloadConfigs
from .util import populateWorkload
import os, subprocess


logger = getLogger(__name__.rsplit(".", 1)[-1])


class KubectlManager:
    __tmp_workload_file = "{}/tmp_workload.yaml".format(user_dir)

    def __init__(self, browser: Browser, workload_configs: WorkloadConfigs):
        self.__browser = browser
        self.__workload_configs = workload_configs

    def operationWorkload(self, cmd, project, namespace, workload):
        workload_file = "{}/{}/{}/{}".format(config.Browser.path, project, namespace, workload)
        configs = self.__workload_configs.getConfig(project, namespace, workload)
        if configs:
            populateWorkload(workload_file, configs, self.__tmp_workload_file)
            workload_file = self.__tmp_workload_file
        cpi = subprocess.run(
            ("kubectl", cmd, "-f", workload_file, "-n", namespace),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        log_msg = "kubectl {c} -f {p}/{n}/{w} -n {n}: {cpi}".format(
            c=cmd,
            p=project,
            n=namespace,
            w=workload,
            cpi=cpi.stdout.decode().rstrip("\n").replace("\n", " - ")
        )
        if cpi.returncode:
            logger.error(log_msg)
        else:
            logger.info(log_msg)
        if os.path.isfile(self.__tmp_workload_file):
            os.remove(self.__tmp_workload_file)
        return "{}/{}/{}".format(project, namespace, workload), cpi.returncode

    def operationNamespaceWorkloads(self, cmd, project, namespace):
        results = list()
        for workload in self.__browser.listWorkloads(project, namespace):
            results.append(self.operationWorkload(cmd, project, namespace, workload))
        return results

    def operationProjectWorkloads(self, cmd, project):
        results = list()
        for namespace in self.__browser.listNamespaces(project):
            results.extend(self.operationNamespaceWorkloads(cmd, project, namespace))
        return results

    def operationAllWorkloads(self, cmd):
        results = list()
        for project in self.__browser.listProjects():
            results.extend(self.operationProjectWorkloads(cmd, project))
        return results

    def getVersion(self):
        try:
            cpi = subprocess.run(("kubectl", "version"), capture_output=True)
            if cpi.stderr:
                logger.error("kubectl version: {}".format(cpi.stderr.decode().rstrip("\n").replace("\n", " ")))
            if cpi.stdout:
                return cpi.stdout.decode()
        except FileNotFoundError:
            logger.error("can't find kubectl")


class HelmManager:
    def __init__(self, browser: Browser, workload_configs: WorkloadConfigs):
        self.__browser = browser
        self.__workload_configs = workload_configs

    def getVersion(self):
        try:
            cpi = subprocess.run(("helm", "version"), capture_output=True)
            if cpi.stderr:
                logger.error("helm version: {}".format(cpi.stderr.decode().rstrip("\n").replace("\n", " ")))
            if cpi.stdout:
                return cpi.stdout.decode()
        except FileNotFoundError:
            logger.error("can't find helm")


class RancherManager:
    def __init__(self, browser: Browser):
        self.__browser = browser
        self.__project_map = dict()

    def login(self):
        if all((config.Rancher.server, config.Rancher.bearer_token, config.Rancher.default_context, config.Rancher.default_context_name)):
            cpi = subprocess.run(
                ("rancher", "login", config.Rancher.server, "--token", config.Rancher.bearer_token, "--context", config.Rancher.default_context),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            log_msg = "rancher login {} --token <hidden> --context {}: {}".format(config.Rancher.server, config.Rancher.default_context, cpi.stdout.decode().rstrip("\n").replace("\n", " - "))
            if cpi.returncode:
                logger.error(log_msg)
            else:
                logger.info(log_msg)
                self.__buildProjectMap()
        else:
            logger.warning("rancher config missing")

    def __buildProjectMap(self):
        if self.__project_map:
            self.__contextSwitch(config.Rancher.default_context_name)
            self.__project_map.clear()
        cpi = subprocess.run(("rancher", "projects", "ls"), capture_output=True)
        if not cpi.returncode and cpi.stdout:
            projects = cpi.stdout.decode().split("\n")
            for line in projects[1:]:
                project = list(filter(None, line.split(" ")))
                if project:
                    self.__project_map[project[1]] = project[0]
            logger.info("rancher projects ls: {}".format(list(self.__project_map.keys())))
        else:
            logger.error("rancher projects ls: {}".format(cpi.stderr.decode().rstrip("\n").replace("\n", " - ")))

    def __contextSwitch(self, project):
        cpi = subprocess.run(("rancher", "context", "switch", self.__project_map[project]), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log_msg = "rancher context switch {}".format(project, cpi.stdout.decode().rstrip("\n").replace("\n", " - "))
        if cpi.returncode:
            logger.error("{}: {}".format(log_msg, cpi.stdout.decode().rstrip("\n").replace("\n", " - ")))
        else:
            logger.info(log_msg)
        return not cpi.returncode

    def __operation(self, cmd, sub_cmd, value):
        cpi = subprocess.run(("rancher", cmd, sub_cmd, value), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        log_msg = "rancher {} {} {}".format(cmd, sub_cmd, value)
        if cpi.returncode:
            logger.error("{}: {}".format(log_msg, cpi.stdout.decode().rstrip("\n").replace("\n", " - ")))
        else:
            logger.info(log_msg)
        return cpi.returncode

    def operationProject(self, cmd, project):
        err = self.__operation("projects", cmd, self.__project_map.setdefault(project, project))
        if not err:
            self.__buildProjectMap()
        return project, err

    def operationNamespace(self, cmd, project, namespace):
        if self.__contextSwitch(project):
            err = self.__operation("namespaces", cmd, namespace)
            return "{}/{}".format(project, namespace), err

    def getVersion(self):
        try:
            cpi = subprocess.run(("rancher", "settings", "get", "server-version"), capture_output=True)
            if cpi.stderr:
                logger.error("rancher settings get server-version: {}".format(cpi.stderr.decode().rstrip("\n").replace("\n", " ")))
            if cpi.stdout:
                return list(filter(None, cpi.stdout.decode().split("\n")))[-1]
        except FileNotFoundError:
            logger.error("can't find rancher cli")
