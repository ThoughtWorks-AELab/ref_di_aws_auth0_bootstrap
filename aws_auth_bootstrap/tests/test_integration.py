from time import time

import boto3

from aws_auth_bootstrap.builders.auth0tools import Auth0Builder, create_auth0_client

client_name = 'testaccount' + str(int(time() * 1000))
account_id = "123-123-123"
saml_provider_name = "auth0-" + client_name
role_hierarchy_rule_name = client_name + "-hierarchy-rule"
github_connection_rule_name = client_name + "-github-rule"
github_connection_name = client_name + "-connection"
fake_github_id = "fake-github-id"
fake_github_secret = "fake-github-secret"


def teardown_function(fn):
    delete_client_by_name(client_name)
    delete_provider_by_name(saml_provider_name)
    delete_rules_by_name(role_hierarchy_rule_name)
    delete_rules_by_name(github_connection_rule_name)
    delete_connection_by_name(github_connection_name)


def test_configure_sso():
    created = Auth0Builder().configure_sso(client_name, account_id, fake_github_id, fake_github_secret)
    assert_saml_is_configured(created['client'])
    assert_github_connection_is_configured(created['client'])
    assert_aws_provider_is_configured(saml_provider_name)


def test_configure_sso_is_idempotent():
    Auth0Builder().configure_sso(client_name, account_id, fake_github_id, fake_github_secret)
    created = Auth0Builder().configure_sso(client_name, account_id, fake_github_id, fake_github_secret)
    assert_saml_is_configured(created['client'])
    assert_aws_provider_is_configured(saml_provider_name)


def test_saml_client_creation_is_idempotent():
    Auth0Builder().create_aws_saml_client(client_name, account_id)
    Auth0Builder().create_aws_saml_client(client_name, account_id)
    assert len(clients_by_name(client_name)) == 1


def test_deploy_rules():
    Auth0Builder().deploy_rules(client_name, {
        "saml_provider_name": saml_provider_name,
        "roles": [
            ("auth0-role-1", "aws-role-1"),
            ("auth0-role-2", "aws-role-2")
        ]
    })
    assert_rules_are_deployed()


def test_deploy_rules_is_idempotent():
    Auth0Builder().deploy_rules(client_name, {
        "saml_provider_name": saml_provider_name,
        "roles": [
            ("auth0-role-1", "aws-role-1"),
            ("auth0-role-2", "aws-role-2")
        ]
    })
    Auth0Builder().deploy_rules(client_name, {
        "saml_provider_name": saml_provider_name,
        "roles": [
            ("auth0-role-1", "aws-role-1"),
            ("auth0-role-2", "aws-role-2")
        ]
    })
    assert_rules_are_deployed()


#
# Utility methods
#
def assert_rule_is_deployed(name, auth0_client=create_auth0_client()):
    rules = list(filter(lambda c: c['name'] == name, auth0_client.rules.all()))
    assert len(rules) == 1
    return rules[0]


def assert_rules_are_deployed():
    hierarchy_rule = assert_rule_is_deployed(role_hierarchy_rule_name)
    connection_rule = assert_rule_is_deployed(github_connection_rule_name)
    assert connection_rule['order'] < hierarchy_rule['order']


def delete_rules_by_name(name, auth0_client=create_auth0_client()):
    for client in filter(lambda c: c['name'] == name, auth0_client.rules.all()):
        auth0_client.rules.delete(client['id'])


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
    for client in clients_by_name(name):
        auth0_client.clients.delete(client['client_id'])


def clients_by_name(name):
    auth0_client = create_auth0_client()
    return list(filter(lambda c: c['name'] == name, auth0_client.clients.all()))


def delete_provider_by_name(name):
    client = boto3.client('iam')
    providers = providers_from_name(name, client)
    for p in providers:
        client.delete_saml_provider(
            SAMLProviderArn=p['Arn']
        )


def connections_by_name(name):
    auth0_client = create_auth0_client()
    return list(filter(lambda c: c['name'] == name, auth0_client.connections.all()))


def delete_connection_by_name(name):
    auth0_client = create_auth0_client()
    for connection in connections_by_name(name):
        auth0_client.connections.delete(connection['id'])


def assert_saml_is_configured(client):
    assert client['addons'] is not None
    assert client['addons']['samlp'] is not None
    assert client['addons']['samlp']['audience'] == 'https://signin.aws.amazon.com/saml'


def assert_github_connection_is_configured(client, auth0_client=create_auth0_client()):
    client_id = client['client_id']
    connections = list(filter(lambda conn: client_id in conn['enabled_clients'] and conn['name'] == github_connection_name, auth0_client.connections.all()))
    print("connections: " + str(connections))
    assert len(connections) == 1
    assert connections[0]['strategy'] == 'github'
    # assert connections[0]['realms'] == ['github'] //TODO: what should this be, if anything?
    assert connections[0]['options']['profile'] == True
    assert connections[0]['options']['client_id'] == fake_github_id
    assert connections[0]['options']['client_secret'] == fake_github_secret

    assert connections[0]['name'] == github_connection_name
