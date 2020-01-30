from assistant.configuration import config, user_dir, static_dir
from assistant.blacklist import BlacklistManger
from assistant.workload import WorkloadConfigs
from assistant.browser import Browser
from assistant import api
import falcon


base_blacklist = BlacklistManger(user_dir, "base_blacklist.txt")
base_blacklist.init()
base_blacklist.read()

blacklist = BlacklistManger(user_dir, "blacklist.txt")
blacklist.init()
blacklist.read()

workload_configs = WorkloadConfigs(user_dir)
workload_configs.init()
workload_configs.read()

browser = Browser(config.Browser.path, base_blacklist, blacklist)
browser.read()


app = falcon.API()

routes = (
    ("/", api.Static("/static/index.html")),
    ("/projects", api.Projects(browser)),
    ("/projects/{project}", api.NameSpaces(browser)),
    ("/projects/{project}/{namespace}", api.Workloads(browser)),
    ("/workload-configs", api.WorkloadConfs(workload_configs)),
    ("/blacklist", api.Blacklist(blacklist)),
    ("/kubeconfig", api.Kubeconfig())
)

for route in routes:
    app.add_route(*route)

app.add_static_route("/static", static_dir)

app.req_options.strip_url_path_trailing_slash = True

# gunicorn --log-level error app:app

