__all__ = ('config', 'user_dir')

from simple_conf import configuration, section
import os


user_dir = '{}/storage'.format(os.getcwd())

static_dir = "{}/static".format(os.path.dirname(os.path.realpath(__file__)))

if not os.path.exists(user_dir):
    os.makedirs(user_dir)


@configuration
class AssistantConf:

    @section
    class Browser:
        path = None

    @section
    class Kubeconfig:
        path = "{}/.kube".format(os.path.expanduser("~"))
        file = "config"

    @section
    class Logger:
        level = "info"
        colored = True
        to_file = True


config = AssistantConf('assistant.conf', user_dir)
