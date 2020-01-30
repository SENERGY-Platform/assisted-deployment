from .configuration import config
from .logger import getLogger
from .browser import Browser
from .blacklist import BlacklistManger
from .workload import WorkloadConfigs
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


class Project:
    def __init__(self, browser: Browser):
        self.__browser = browser

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, project):
        try:
            item = self.__browser.getProject(project)
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(item)
        except KeyError:
            resp.status = falcon.HTTP_404
        except Exception:
            resp.status = falcon.HTTP_500


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


class NameSpace:
    def __init__(self, browser: Browser):
        self.__browser = browser

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, project, namespace):
        try:
            item = self.__browser.getNamespace(project, namespace)
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(item)
        except KeyError:
            resp.status = falcon.HTTP_404
        except Exception:
            resp.status = falcon.HTTP_500


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


class Workload:
    def __init__(self, browser: Browser):
        self.__browser = browser

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, project, namespace, workload):
        try:
            item = self.__browser.getWorkload(project, namespace, workload)
            resp.status = falcon.HTTP_200
            resp.content_type = falcon.MEDIA_JSON
            resp.body = json.dumps(item)
        except KeyError:
            resp.status = falcon.HTTP_404
        except Exception:
            resp.status = falcon.HTTP_500


class Control:
    def __init__(self, browser: Browser, blacklist: BlacklistManger):
        self.__browser = browser
        self.__blacklist = blacklist

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response, option):
        if option == "reload":
            self.__blacklist.read()
            self.__browser.read()
            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_404


class Blacklist:
    def __init__(self, blacklist: BlacklistManger):
        self.__blacklist = blacklist

    def on_get(self, req: falcon.request.Request, resp: falcon.response.Response):
        resp.status = falcon.HTTP_200
        resp.content_type = falcon.MEDIA_JSON
        resp.body = json.dumps(self.__blacklist.list())

    def on_put(self, req: falcon.request.Request, resp: falcon.response.Response):
        if not req.content_type == falcon.MEDIA_JSON:
            resp.status = falcon.HTTP_415
        else:
            try:
                items = json.load(req.bounded_stream)
                self.__blacklist.update(items)
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
        if not req.content_type == falcon.MEDIA_TEXT:
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
        if not req.content_type == falcon.MEDIA_TEXT:
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

