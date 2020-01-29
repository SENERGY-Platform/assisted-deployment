__all__ = ("WorkloadConfigs",)


from .logger import getLogger
from .util import loadYamlFile, dumpYamlFile
import os


logger = getLogger(__name__.rsplit(".", 1)[-1])


class WorkloadConfigs:
    def __init__(self, path):
        self.__path = path
        self.__wl_conf_file = "wl_conf_file.yaml"
        self.__configs = dict()

    def init(self):
        if not os.path.isfile("{}/{}".format(self.__path, self.__wl_conf_file)):
            try:
                with open("{}/{}".format(self.__path, self.__wl_conf_file), "w+") as file:
                    logger.info("created workload config at '{}/{}'".format(self.__path, self.__wl_conf_file))
            except Exception as ex:
                logger.error("could not create workload config at '{}/{}' - {}".format(self.__path, self.__wl_conf_file, ex))

    def read(self):
        logger.info("reading workload configs from '{}/{}'".format(self.__path, self.__wl_conf_file))
        try:
            data = loadYamlFile("{}/{}".format(self.__path, self.__wl_conf_file))
            if data and type(data[0]) is dict:
                self.__configs.clear()
                self.__configs.update(data[0])
        except Exception as ex:
            logger.error("could nor read workload configs from '{}/{}'".format(self.__path, self.__wl_conf_file))

    def getConfig(self, project, namespace, workload):
        try:
            return self.__configs[project][namespace][workload].copy()
        except KeyError as ex:
            logger.error("could not get config for {}/{}/{} - {}".format(project, namespace, workload, ex))
            raise
