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


import yaml


def loadYamlFile(path):
    parts = list()
    with open(path, "r") as file:
        for data in yaml.load_all(file, Loader=yaml.SafeLoader):
            parts.append(data)
    return parts

def dumpYamlFile(parts: list, path):
    with open(path, "w") as file:
        yaml.dump_all(parts, stream=file)

def setKubeconfig(path, config):
    with open(path, "w") as file:
        file.write(config)

def getKubeconfig(path) -> str:
    with open(path, "r") as file:
        return file.read()

def populateWorkload(workload, configs, output):
    with open(workload, "r") as org_file:
        with open(output, "w") as tmp_file:
            for line in org_file:
                for key, value in configs.items():
                    if key in line:
                        line = line.replace(key, value)
                tmp_file.write(line)
