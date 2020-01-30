__all__ = ("Browser",)


from .logger import getLogger
from .blacklist import BlacklistManger
import os


logger = getLogger(__name__.rsplit(".", 1)[-1])


class Browser:
    def __init__(self, path, base_blacklist: BlacklistManger, blacklist: BlacklistManger):
        self.__path = path
        self.__base_blacklist = base_blacklist
        self.__blacklist = blacklist
        self.__projects = dict()

    def read(self):
        self.__projects.clear()
        logger.info("loading projects from '{}'".format(self.__path))
        for pr in os.listdir(self.__path):
            if not self.__blacklist.check(pr) and not self.__base_blacklist.check(pr) and os.path.isdir("{}/{}".format(self.__path, pr)):
                project = dict()
                for np in os.listdir("{}/{}".format(self.__path, pr)):
                    if not self.__blacklist.check("{}/{}".format(pr, np)) and not self.__base_blacklist.check(np) and os.path.isdir("{}/{}/{}".format(self.__path, pr, np)):
                        workloads = dict()
                        for wl in os.listdir("{}/{}/{}".format(self.__path, pr, np)):
                            if any(extension in wl for extension in (".yml", ".yaml")):
                                workloads[wl.split(".", 1)[0]] = "{}/{}/{}/{}".format(self.__path, pr, np, wl)
                        project[np] = workloads
                self.__projects[pr] = project
                logger.debug("project '{}': {}".format(pr, list(project.keys())))

    def getProject(self, project) -> dict:
        try:
            return self.__projects[project]
        except KeyError as ex:
            logger.error("could not get project - {}".format(ex))
            raise

    def listProjects(self) -> list:
        projects = list(self.__projects.keys())
        projects.sort()
        return projects

    def getNamespace(self, project, namespace):
        try:
            return self.__projects[project][namespace]
        except KeyError as ex:
            logger.error("could not get name space - {}".format(ex))
            raise

    def listNamespaces(self, project) -> list:
        try:
            namespaces = list(self.__projects[project].keys())
            namespaces.sort()
            return namespaces
        except KeyError as ex:
            logger.error("could not list name spaces - {}".format(ex))
            raise

    def getWorkload(self, project, name_space, name) -> str:
        try:
            return self.__projects[project][name_space][name]
        except KeyError as ex:
            logger.error("could not get workload - {}".format(ex))
            raise

    def listWorkloads(self, project, namespace) -> list:
        try:
            workloads = list(self.__projects[project][namespace].values())
            workloads.sort()
            return workloads
        except KeyError as ex:
            logger.error("could not list workloads - {}".format(ex))
            raise
