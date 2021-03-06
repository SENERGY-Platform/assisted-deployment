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
            logger.error("could not read workload configs from '{}/{}' - {}".format(self.__path, self.__wl_conf_file, ex))

    def __write(self):
        logger.info("writing workload configs to '{}/{}'".format(self.__path, self.__wl_conf_file))
        try:
            dumpYamlFile([self.__configs], "{}/{}".format(self.__path, self.__wl_conf_file))
        except Exception as ex:
            logger.error("could not write workload configs to '{}/{}' - {}".format(self.__path, self.__wl_conf_file, ex))

    def getConfig(self, project, namespace, workload):
        try:
            return self.__configs[project][namespace][workload].copy()
        except KeyError:
            pass

    def list(self):
        return self.__configs.copy()

    def update(self, data):
        self.__configs.clear()
        self.__configs.update(data)
        self.__write()
