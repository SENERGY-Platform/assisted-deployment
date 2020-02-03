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
