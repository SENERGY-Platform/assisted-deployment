__all__ = ("loadYamlFile", "dumpYamlFile")


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
