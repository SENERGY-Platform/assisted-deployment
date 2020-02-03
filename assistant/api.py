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

from .configuration import config
from .logger import getLogger
from .browser import Browser
from .blacklist import BlacklistManger
from .workload import WorkloadConfigs
from .deployment import KubectlManager
from .util import getKubeconfig, setKubeconfig
import falcon, json, yaml


logger = getLogger(__name__.rsplit(".", 1)[-1])


class Static:
    def __init__(self, location):
        self.__location = location

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        raise falcon.HTTPPermanentRedirect(self.__location)


class Projects:
    def __init__(self, browser: Browser):
        self.__browser = browser

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        try:
            items = self.__browser.listProjects()
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(items)
        except Exception:
            resp.status = falcon.HTTP_404


class NameSpaces:
    def __init__(self, browser: Browser):
        self.__browser = browser

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, project):
        try:
            items = self.__browser.listNamespaces(project)
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(items)
        except Exception:
            resp.status = falcon.HTTP_404


class Workloads:
    def __init__(self, browser: Browser):
        self.__browser = browser

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, project, namespace):
        try:
            items = self.__browser.listWorkloads(project, namespace)
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(items)
        except Exception:
            resp.status = falcon.HTTP_404


class Blacklist:
    def __init__(self, blacklist: BlacklistManger):
        self.__blacklist = blacklist

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_TEXT
        resp.body = "\n".join(self.__blacklist.list())

    def on_put(self, req: falcon.request.Request, resp: falcon.response.Response):
        if not req.content_type in ("text/plain;charset=UTF-8", falcon.MEDIA_TEXT):
            resp.status = falcon.HTTP_415
        else:
            try:
                data = req.bounded_stream.read()
                data = [item for item in data.decode().split("\n") if item]
                self.__blacklist.update(data)
                resp.status = falcon.HTTP_200
            except Exception as ex:
                logger.error("could not update blacklist - {}".format(ex))
                resp.status = falcon.HTTP_500


class Kubeconfig:
    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        try:
            kubeconfig = getKubeconfig("{}/{}".format(config.Kubeconfig.path, config.Kubeconfig.file))
            if kubeconfig:
                resp.status = falcon.HTTP_200
                resp.content_type = falcon.MEDIA_TEXT
                resp.body = kubeconfig
            else:
                resp.status = falcon.HTTP_404
        except Exception as ex:
            logger.error("can't get kubeconfig at '{}/{}' - {}".format(config.Kubeconfig.path, config.Kubeconfig.file, ex))
            resp.status = falcon.HTTP_500

    def on_put(self, req: falcon.request.Request, resp: falcon.response.Response):
        if not req.content_type in ("text/plain;charset=UTF-8", falcon.MEDIA_TEXT):
            resp.status = falcon.HTTP_415
        else:
            try:
                data = req.bounded_stream.read()
                if data:
                    setKubeconfig("{}/{}".format(config.Kubeconfig.path, config.Kubeconfig.file), data.decode())
                    resp.status = falcon.HTTP_200
                else:
                    resp.status = falcon.HTTP_400
            except Exception as ex:
                logger.error("can't write kubeconfig to '{}/{}' - {}".format(config.Kubeconfig.path, config.Kubeconfig.file, ex))
                resp.status = falcon.HTTP_500


class WorkloadConfs:
    def __init__(self, workload_configs: WorkloadConfigs):
        self.__workload_configs = workload_configs

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        try:
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_TEXT
            resp.body = yaml.dump(self.__workload_configs.list())
        except Exception as ex:
            logger.error("can't list workload configs - {}".format(ex))
            resp.status = falcon.HTTP_500

    def on_put(self, req: falcon.request.Request, resp: falcon.response.Response):
        if not req.content_type in ("text/plain;charset=UTF-8", falcon.MEDIA_TEXT):
            resp.status = falcon.HTTP_415
        else:
            try:
                data = req.bounded_stream.read()
                if data:
                    self.__workload_configs.update(yaml.load(data.decode(), Loader=yaml.SafeLoader))
                    resp.status = falcon.HTTP_200
                else:
                    resp.status = falcon.HTTP_400
            except Exception as ex:
                logger.error("can't update workload configs - {}".format(ex))
                resp.status = falcon.HTTP_500


class Kubectl:

    class Operation:
        __parameters = ("project", "namespace", "workload")

        def __init__(self, kubectl_manager: KubectlManager):
            self.__kubectl_manager = kubectl_manager

        def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
            if req.params and set(req.params).issubset(self.__parameters):
                if len(req.params) == 3:
                    try:
                        resp.body = json.dumps(list(self.__kubectl_manager.operationWorkload(req.path.rsplit("/", 1)[-1], **req.params)))
                        resp.status = falcon.HTTP_200
                    except Exception:
                        resp.status = falcon.HTTP_400
                elif len(req.params) == 2:
                    try:
                        resp.body = json.dumps(self.__kubectl_manager.operationNamespaceWorkloads(req.path.rsplit("/", 1)[-1], **req.params))
                        resp.status = falcon.HTTP_200
                    except Exception:
                        resp.status = falcon.HTTP_400
                elif len(req.params) == 1:
                    try:
                        if "*" in req.params.values():
                            resp.body = json.dumps(self.__kubectl_manager.operationAllWorkloads(req.path.rsplit("/", 1)[-1]))
                        else:
                            resp.body = json.dumps(self.__kubectl_manager.operationProjectWorkloads(req.path.rsplit("/", 1)[-1], **req.params))
                        resp.status = falcon.HTTP_200
                    except Exception:
                        resp.status = falcon.HTTP_400
            else:
                resp.status = falcon.HTTP_400

    class Version:
        def __init__(self, kubectl_manager: KubectlManager):
            self.__kubectl_manager = kubectl_manager

        def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
            version = self.__kubectl_manager.getVersion()
            if version:
                resp.body = version
                resp.status = falcon.HTTP_200
            else:
                resp.status = falcon.HTTP_404
