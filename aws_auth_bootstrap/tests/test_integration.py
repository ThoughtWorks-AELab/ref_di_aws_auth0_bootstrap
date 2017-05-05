from time import time

from aws_auth_bootstrap.auth0.auth0tools import create_aws_saml_client, create_auth0_client

client_name = 'testaccount' + str(int(time() * 1000))
account_id = "123-123-123"


def teardown_function(fn):
    delete_client_by_name(client_name)


def test_create_saml_configuration():
    created_client = create_aws_saml_client(client_name, account_id)
    assert_saml_is_configured(created_client)


#
# Utility methods
#

def delete_client_by_name(name):
    auth0_client = create_auth0_client()
    for client in filter(lambda c: c['name'] == name, auth0_client.clients.all()):
        auth0_client.clients.delete(client['client_id'])


def assert_saml_is_configured(client):
    assert client['addons'] is not None
    assert client['addons']['samlp'] is not None
    assert client['addons']['samlp']['audience'] == 'https://signin.aws.amazon.com/saml'
