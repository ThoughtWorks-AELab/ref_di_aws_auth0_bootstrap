import json

from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
import os
import pkg_resources
import boto3
import urllib.request

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


def create_aws_saml_client(client_name, account_id):
    create_client_request = json.loads(
        pkg_resources.resource_string(resource_package, 'resources/base-auth0-client-message.json'))
    create_client_request['name'] = client_name
    create_client_request['client_metadata'] = {
        "aws_account_number": account_id
    }
    return create_auth0_client().clients.create(create_client_request)


def configure_sso(client_name, account_id):
    # TODO: make this idempotent so if one exists, it still builds the other
    new_client = create_aws_saml_client(client_name, account_id)
    new_provider = create_aws_saml_provider(new_client['client_id'], "auth0-" + client_name)
    return {"client": new_client, "provider": new_provider}


def get_saml_metadata_document(auth0_host, client_id):
    # TODO: check return code
    return urllib.request.urlopen(f"https://{auth0_host}/samlp/metadata/{client_id}").read().decode("utf-8")


def create_aws_saml_provider(client_id, name):
    saml_metadata_document = get_saml_metadata_document(auth0_client_config()['domain'], client_id)
    return boto3.client('iam').create_saml_provider(
        SAMLMetadataDocument=saml_metadata_document,
        Name=name)
