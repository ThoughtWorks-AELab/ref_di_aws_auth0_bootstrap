from time import time

from aws_auth_bootstrap.auth0.auth0tools import create_aws_saml_client, create_auth0_client

account_name = 'testaccount' + str(int(time() * 1000))
account_id = "123-123-123"


class TestIntegration:
    def setup_method(self):
        self.created_client_id = None
        pass

    def teardown_method(self):
        auth0_client = create_auth0_client()
        if self.created_client_id:
            delete_client(self.created_client_id, auth0_client)

    def test_create_saml_configuration(self):
        created_client = create_aws_saml_client(account_name, account_id)
        self.created_client_id = created_client['client_id']
        assert_saml_is_configured(created_client)


#
# Utility methods
#

def delete_client(id, auth0_client):
    auth0_client.clients.delete(id)


def assert_saml_is_configured(client):
    assert client['addons'] is not None
    assert client['addons']['samlp'] is not None
    assert client['addons']['samlp']['audience'] == 'https://signin.aws.amazon.com/saml'
