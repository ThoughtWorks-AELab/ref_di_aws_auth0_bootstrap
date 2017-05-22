import os
import shutil
import subprocess
from copy import copy

from aws_auth_bootstrap.builders.auth0tools import Auth0Builder
from aws_auth_bootstrap.builders.github_builder import GithubBuilder

resource_package = __name__


class Bootstrap:
    def __init__(self, environ=os.environ):
        self.environ = environ
        self.check_for_terraform()

    def run(self, config):

        github_builder = GithubBuilder(config['github'])
        for role in config['roles']:
            github_builder.create_team(role['idp_role'], [])

        auth0builder = Auth0Builder(config["idp"])

        def add_org_name(mapping):
            org_name = config['github']['github_organization']
            new_mapping = copy(mapping)
            new_mapping['idp_role'] = f"{org_name}/{mapping['idp_role']}"
            return new_mapping

        account_configs = self.configure_accounts(auth0builder, config)
        client_ids = map(lambda account_config: account_config['client']['clientID'], account_configs)

        auth0builder.deploy_rules(config['project_name'], {
            "client_ids": client_ids,
            "saml_provider_name": config['saml_provider_name'],
            "roles": map(lambda role_mapping: add_org_name(role_mapping), config['roles'])
        })

    def configure_accounts(self, auth0builder, config):
        accounts = config["accounts"]
        idp = config['idp']
        github = config['github']
        account_configs = []
        for account in accounts:
            account_config = auth0builder.configure_sso(account['name'],
                                       account['aws_account_number'],
                                       github['github_client_id'],
                                       github['github_client_secret'])
            account_configs.append(account_config)
            self.build_policies(
                account['terraform_dir'],
                account, config["project_name"],
                config['saml_provider_name'],
                idp['domain']
            )
        return account_configs

    def expect_success(self, return_code):
        if return_code != 0:
            raise Exception("Command failed.")

    def build_policies(self, terraform_dir, account, project_name, saml_provider_name, saml_aud):

        power_user_roles = self.build_role_list(account['role_mapping']['poweruser'])
        readonly_roles = self.build_role_list(account['role_mapping']['readonly'])

        bucket_name = f"{project_name}-{account['name']}"

        command = ["terraform", "init", "-backend=true",
                   f"-backend-config=bucket={bucket_name}",
                   "-lock=true",
                   "-force-copy",
                   f"-backend-config=key=bootstrap/bootstrap.tfstate",
                   f"-backend-config=region={account['region']}",
                   f"-backend-config=access_key={account['aws_access_key_id']}",
                   f"-backend-config=secret_key={account['aws_secret_access_key']}",
                   ]

        process = subprocess.Popen(command,
                                   cwd=f"{os.path.dirname(os.path.realpath(__file__))}/resources/terraform/{terraform_dir}")
        self.expect_success(process.wait())

        process = subprocess.Popen(["terraform", "apply",
                                    "-var", f"""aws_access_key={account['aws_access_key_id']}""",
                                    "-var", f"""aws_secret_key={account['aws_secret_access_key']}""",
                                    "-var", f"""env_name={project_name}""",
                                    "-var", f"""power_user_roles={power_user_roles}""",
                                    "-var", f"""readonly_roles={readonly_roles}""",
                                    "-var", f"""aws_saml_provider={saml_provider_name}""",
                                    "-var", f"""saml_aud={saml_aud}""",
                                    ],
                                   cwd=f"{os.path.dirname(os.path.realpath(__file__))}/resources/terraform/{terraform_dir}")
        self.expect_success(process.wait())

    def check_for_terraform(self):
        if shutil.which('terraform') is None:
            raise Exception("Terraform must be on the class path")

    def build_role_list(self, role_array):
        return ", ".join(role_array)
