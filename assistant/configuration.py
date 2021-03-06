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


from simple_conf import configuration, section
import os


user_dir = '{}/storage'.format(os.getcwd())

static_dir = "{}/static".format(os.path.dirname(os.path.realpath(__file__)))

if not os.path.exists(user_dir):
    os.makedirs(user_dir)


@configuration
class AssistantConf:

    @section
    class Assistant:
        name = "My Assistant"

    @section
    class Browser:
        path = "/source"

    @section
    class Kubeconfig:
        path = "{}/.kube".format(os.path.expanduser("~"))
        file = "config"

    @section
    class Rancher:
        server = None
        default_context = None
        default_context_name = "Default"
        bearer_token = None

    @section
    class Logger:
        level = "info"
        colored = False
        to_file = False


config = AssistantConf('assistant.conf', user_dir, ext_aft_crt=False)
