import json

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
import os
import pkg_resources

resource_package = __name__


def auth0_client_config():
    return {
        "domain": os.environ['AUTH0_HOST'] + ".auth0.com",
        "client_id": os.environ['AUTH0_CLIENT_ID'],
        "client_secret": os.environ['AUTH0_CLIENT_SECRET']
    }


def create_auth0_client(config=auth0_client_config()):
    domain = config["domain"]
    token = GetToken(domain).client_credentials(config["client_id"],
                                                 config["client_secret"], f"https://{domain}/api/v2/")
    return Auth0(domain, token['access_token'])


def create_aws_saml_client(account_name, account_id):
    create_client_request = json.loads(
        pkg_resources.resource_string(resource_package, 'resources/base-auth0-client-message.json'))
    create_client_request['name'] = account_name
    create_client_request['client_metadata'] = {
        "aws_account_number": account_id
    }
    return create_auth0_client().clients.create(create_client_request)