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
import os


logger = getLogger(__name__.rsplit(".", 1)[-1])


class BlacklistError(Exception):
    pass


class BlacklistManger:
    def __init__(self, path, file):
        self.__file = "{}/{}".format(path, file)
        self.__list = list()

    def init(self):
        if not os.path.isfile(self.__file):
            try:
                with open(self.__file, "w+") as file:
                    logger.info("created blacklist at '{}'".format(self.__file))
            except Exception as ex:
                logger.error("could not create blacklist at '{}' - {}".format(self.__file, ex))
                # raise BlacklistError(ex)

    def read(self):
        logger.info("reading blacklist from '{}'".format(self.__file))
        try:
            with open(self.__file, "r") as file:
                self.__list.clear()
                for line in file:
                    self.__list.append(line.replace("\n", ""))
        except Exception as ex:
            logger.error("could not read blacklist - {}".format(ex))
            # raise BlacklistError(ex)

    def __write(self):
        logger.info("writing blacklist to '{}'".format(self.__file))
        try:
            with open(self.__file, "w") as file:
                for item in self.__list:
                    file.write(item)
                    file.write("\n")
        except Exception as ex:
            logger.error("could not write blacklist - {}".format(ex))
            # raise BlacklistError(ex)

    def check(self, item: str) -> bool:
        if item in self.__list:
            return True
        return False

    def list(self) -> list:
        return self.__list.copy()

    def update(self, items: list):
        self.__list.clear()
        self.__list.extend(items)
        self.__write()
