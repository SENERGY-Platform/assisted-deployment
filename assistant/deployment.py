from .configuration import config, user_dir
from .logger import getLogger
from .browser import Browser
from .workload import WorkloadConfigs
from .util import populateWorkload
import os


logger = getLogger(__name__.rsplit(".", 1)[-1])


class KubectlManager:
    def __init__(self, browser: Browser, workload_configs: WorkloadConfigs):
        self.__browser = browser
        self.__workload_configs = workload_configs

    def deployWorkload(self, project, namespace, workload):
        configs = self.__workload_configs.getConfig(project, namespace, workload)
        if configs:
            populateWorkload("{}/{}/{}/{}".format(config.Browser.path, project, namespace, workload), configs, "{}/tmp_wl.yaml".format(user_dir))
            print("kubectl apply -f {}/tmp_wl.yaml --namespace={}".format(user_dir, namespace))
            os.remove("{}/tmp_wl.yaml".format(user_dir))
        else:
            print("kubectl apply -f {}/{}/{}/{} --namespace={}".format(config.Browser.path, project, namespace, workload, namespace))

    def deployNamespace(self, project, namespace):
        for workload in self.__browser.listWorkloads(project, namespace):
            self.deployWorkload(project, namespace, workload)

    def deployProject(self, project):
        for namespace in self.__browser.listNamespaces(project):
            self.deployNamespace(project, namespace)

    def deployAll(self):
        for project in self.__browser.listProjects():
            self.deployProject(project)
