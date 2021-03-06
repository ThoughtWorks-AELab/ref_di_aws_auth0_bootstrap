resource_package = __name__

import pkg_resources

class GithubConnectionRuleScriptGenerator:
    def __init__(self):
        self.script = str(pkg_resources.resource_string(resource_package, 'resources/github_connection.js'), "utf=8")

    def generate(self, config):
        user_agent = config['user_agent']
        return self.script.replace("${USER_AGENT}", user_agent)
