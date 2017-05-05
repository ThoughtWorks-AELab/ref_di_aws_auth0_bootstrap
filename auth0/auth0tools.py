import json

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
import os
import pkg_resources

resource_package = __name__


def create_auth0_client():
    domain = os.environ['AUTH0_DOMAIN']
    client_id = os.environ['AUTH0_CLIENT_ID']
    client_secret = os.environ['AUTH0_CLIENT_SECRET']

    token = GetToken(domain).client_credentials(client_id,
                                                client_secret, f"https://{domain}/api/v2/")
    return Auth0(domain, token['access_token'])


def configure_aws_account(account_name, account_id):
    create_client_request = json.loads(
        pkg_resources.resource_string(resource_package, 'resources/base-auth0-client-message.json'))
    create_client_request['name'] = account_name
    create_client_request['client_metadata'] = {
        "aws_account_number": account_id
    }
    print(create_client_request)
    create_auth0_client().clients.create(create_client_request)
