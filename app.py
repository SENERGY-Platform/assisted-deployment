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


from assistant.configuration import config, user_dir, static_dir
from assistant.blacklist import BlacklistManger
from assistant.workload import WorkloadConfigs
from assistant.browser import Browser
from assistant.deployment import KubectlManager, HelmManager, RancherManager
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

kubectl_manager = KubectlManager(browser, workload_configs)
helm_manager = HelmManager(browser, workload_configs)
rancher_manager = RancherManager(browser)
rancher_manager.init()


app = falcon.API()

app.req_options.strip_url_path_trailing_slash = True

routes = (
    ("/", api.Static("/static/panel.html")),
    ("/projects", api.Projects(browser)),
    ("/projects/{project}", api.NameSpaces(browser)),
    ("/projects/{project}/{namespace}", api.Workloads(browser)),
    ("/workload-configs", api.WorkloadConfs(workload_configs)),
    ("/blacklists/source", api.Blacklist(blacklist)),
    ("/blacklists/base", api.Blacklist(base_blacklist)),
    ("/kubeconfig", api.Kubeconfig()),
    ("/kubectl", api.Kubectl(kubectl_manager))
)

for route in routes:
    app.add_route(*route)

app.add_static_route("/static", static_dir)
