import os

from aws_auth_bootstrap.bootstrap import Bootstrap

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
        {
            "idp_role": "ThoughtWorks-AELab/dev_admin",
            "aws_role": "dev_admin"
        },
        {
            "idp_role": "ThoughtWorks-AELab/infra_reader",
            "aws_role": "infra_reader"
        }
    ]
}

Bootstrap().run(sso_config)
