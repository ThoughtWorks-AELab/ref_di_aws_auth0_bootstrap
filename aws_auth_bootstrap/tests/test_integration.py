from time import time

import boto3

from aws_auth_bootstrap.auth0.auth0tools import configure_sso, create_auth0_client

client_name = 'testaccount' + str(int(time() * 1000))
account_id = "123-123-123"
saml_provider_name = "auth0-" + client_name


def teardown_function(fn):
    delete_client_by_name(client_name)
    delete_provider_by_name(saml_provider_name)


def test_configure_sso():
    created = configure_sso(client_name, account_id)
    assert_saml_is_configured(created['client'])
    assert_aws_provider_is_configured(saml_provider_name)


#
# Utility methods
#
def assert_aws_provider_is_configured(provider_name):
    client = boto3.client('iam')
    provider_arns = providers_from_name(provider_name, client)
    providers = list(map(lambda p: client.get_saml_provider(SAMLProviderArn=p['Arn']),
                         provider_arns))
    assert len(providers) == 1


def providers_from_name(provider_name, client):
    return list(filter(lambda provider: provider["Arn"].endswith(provider_name),
                       client.list_saml_providers()['SAMLProviderList']))


def delete_client_by_name(name):
    auth0_client = create_auth0_client()
    for client in filter(lambda c: c['name'] == name, auth0_client.clients.all()):
        auth0_client.clients.delete(client['client_id'])


def delete_provider_by_name(name):
    client = boto3.client('iam')
    providers = providers_from_name(name, client)
    for p in providers:
        client.delete_saml_provider(
            SAMLProviderArn=p['Arn']
        )


def assert_saml_is_configured(client):
    assert client['addons'] is not None
    assert client['addons']['samlp'] is not None
    assert client['addons']['samlp']['audience'] == 'https://signin.aws.amazon.com/saml'
