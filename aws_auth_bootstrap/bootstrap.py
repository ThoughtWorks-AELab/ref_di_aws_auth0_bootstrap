import os
import shutil
import subprocess

from aws_auth_bootstrap.builders.auth0tools import Auth0Builder, create_auth0_client

resource_package = __name__

sso_config = {
    "project_name": "reference-implementation",
    "saml_provider_name": "auth0-preproduction",
    "idp": {
        "domain": os.environ['AUTH0_HOST'] + ".auth0.com",
        "client_id": os.environ['AUTH0_CLIENT_ID'],
        "client_secret": os.environ['AUTH0_CLIENT_SECRET'],
        "github_client_id": os.environ['GITHUB_CLIENT_ID'],
        "github_client_secret": os.environ['GITHUB_CLIENT_SECRET']
    },
    "accounts": [
        {
            "name": "preproduction",
            "region": "us-west-2",
            "aws_account_number": os.environ['PREPROD_AWS_ACCOUNT_NUMBER'],
            "aws_access_key_id": os.environ['PREPROD_AWS_ACCESS_ID'],
            "aws_secret_access_key": os.environ['PREPROD_SECRET_ACCESS_KEY'],
            "terraform_dir": 'preproduction',
            "role_mapping": {
                "poweruser": ["dev_admin"],
                "readonly": ["infra_reader"]
            }
        },
        # {
        #     "name": "production",
        #     "aws_account_number": os.environ['PROD_AWS_ACCOUNT_NUMBER'],
        #     "aws_access_key_id": os.environ['PROD_AWS_ACCESS_ID'],
        #     "aws_secret_access_key": os.environ['PROD_SECRET_ACCESS_KEY'],
        #     "terraform": pkg_resources.resource_string(resource_package, 'resources/production')
        # }
    ],
    "roles": [
        ("ThoughtWorks-AELab/dev_admin", "dev_admin"),
        ("ThoughtWorks-AELab/infra_reader", "infra_reader")
    ]
}


class Bootstrap:
    def __init__(self, environ=os.environ):
        self.environ = environ
        self.check_for_terraform()

    def run(self, config):
        auth0builder = Auth0Builder(create_auth0_client(config["idp"]))

        auth0builder.deploy_rules(sso_config['project_name'], {
            "saml_provider_name": sso_config['saml_provider_name'],
            "roles": sso_config['roles']
        })

        accounts = config["accounts"]
        idp = config['idp']
        for account in accounts:
            auth0builder.configure_sso(account['name'], account['aws_account_number'], idp['github_client_id'],
                                       idp['github_client_secret'])
            self.build_policies(account['terraform_dir'], account, config["project_name"])

    def expect_success(self, return_code):
        if return_code != 0:
            raise Exception("Command failed.")

    def build_policies(self, terraform_dir, account, project_name):

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
                                    ],
                                   cwd=f"{os.path.dirname(os.path.realpath(__file__))}/resources/terraform/{terraform_dir}")
        self.expect_success(process.wait())

    def check_for_terraform(self):
        if shutil.which('terraform') is None:
            raise Exception("Terraform must be on the class path")

    def build_role_list(self, role_array):
        return ", ".join(role_array)


Bootstrap().run(sso_config)
