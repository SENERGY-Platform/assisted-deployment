from assistant.configuration import config, user_dir, static_dir
from assistant.blacklist import BlacklistManger
from assistant.workload import WorkloadConfigs
from assistant.browser import Browser
from assistant import api
import falcon


blacklist = BlacklistManger(user_dir)
blacklist.init()
blacklist.read()

workload_configs = WorkloadConfigs(user_dir)
workload_configs.init()
workload_configs.read()

browser = Browser(config.Browser.path, blacklist)
browser.read()


app = falcon.API()

# routes = (
#     ("/projects", api.Projects(browser)),
#     ("/projects/{project}", api.Project(browser)),
#     ("/projects/{project}/namespaces", api.NameSpaces(browser)),
#     ("/projects/{project}/namespaces/{namespace}", api.NameSpace(browser)),
#     ("/projects/{project}/namespaces/{namespace}/workloads", api.Workloads(browser)),
#     ("/projects/{project}/namespaces/{namespace}/workloads/{workload}", api.Workload(browser)),
#     ("/control/{option}", api.Control(browser, blacklist)),
#     ("/blacklist", api.Blacklist(blacklist)),
#     ("/kubeconfig", api.Kubeconfig())
# )

routes = (
    ("/", api.Static("/static/index.html")),
    ("/projects", api.Projects(browser)),
    ("/projects/{project}", api.NameSpaces(browser)),
    ("/projects/{project}/{namespace}", api.Workloads(browser)),
    ("/control/{option}", api.Control(browser, blacklist)),
    ("/blacklist", api.Blacklist(blacklist)),
    ("/kubeconfig", api.Kubeconfig())
)

for route in routes:
    app.add_route(*route)

app.add_static_route("/static", static_dir)

app.req_options.strip_url_path_trailing_slash = True

# gunicorn --log-level error app:app

