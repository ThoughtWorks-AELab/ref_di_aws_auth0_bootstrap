import os
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

CONFIG = {
    "domain": os.environ['AUTH0_HOST'] + ".auth0.com",
    "client_id": os.environ['AUTH0_CLIENT_ID'],
    "client_secret": os.environ['AUTH0_CLIENT_SECRET']
}

AUTH0_CLIENT = create_auth0_client(CONFIG)


def teardown_function(fn):
    delete_client_by_name(client_name)
    delete_provider_by_name(saml_provider_name)
    delete_rules_by_name(role_hierarchy_rule_name)
    delete_rules_by_name(github_connection_rule_name)
    delete_connection_by_name(github_connection_name)


def test_configure_sso():
    created = Auth0Builder(CONFIG).configure_sso(client_name, account_id, fake_github_id, fake_github_secret)
    assert_saml_is_configured(created['client'])
    assert_github_connection_is_configured(created['client'])
    assert_aws_provider_is_configured(saml_provider_name)


def test_configure_sso_is_idempotent():
    Auth0Builder(CONFIG).configure_sso(client_name, account_id, fake_github_id, fake_github_secret)
    created = Auth0Builder(CONFIG).configure_sso(client_name, account_id, fake_github_id, fake_github_secret)
    assert_saml_is_configured(created['client'])
    assert_aws_provider_is_configured(saml_provider_name)


def test_saml_client_creation_is_idempotent():
    Auth0Builder(CONFIG).create_aws_saml_client(client_name, account_id)
    Auth0Builder(CONFIG).create_aws_saml_client(client_name, account_id)
    assert len(clients_by_name(client_name)) == 1


def test_deploy_rules():
    Auth0Builder(CONFIG).deploy_rules(client_name, {
        "saml_provider_name": saml_provider_name,
        "roles": [
            ("git-group/github-role-1", "aws-role-1"),
            ("git-group/github-role-2", "aws-role-2")
        ]
    })
    assert_rules_are_deployed()


def test_deploy_rules_is_idempotent():
    Auth0Builder(CONFIG).deploy_rules(client_name, {
        "saml_provider_name": saml_provider_name,
        "roles": [
            ("git-group/github-role-1", "aws-role-1"),
            ("git-group/github-role-2", "aws-role-2")
        ]
    })
    Auth0Builder(CONFIG).deploy_rules(client_name, {
        "saml_provider_name": saml_provider_name,
        "roles": [
            ("git-group/github-role-1", "aws-role-1"),
            ("git-group/github-role-2", "aws-role-2")
        ]
    })
    assert_rules_are_deployed()


#
# Utility methods
#
def assert_rule_is_deployed(name):
    # TODO: be nice to have a bit more assurance here. We do have the ability to pull the rule down
    # TODO: and run it with execjs. Could do that....
    rules = list(filter(lambda c: c['name'] == name, AUTH0_CLIENT.rules.all()))
    assert len(rules) == 1
    return rules[0]


def assert_rules_are_deployed():
    hierarchy_rule = assert_rule_is_deployed(role_hierarchy_rule_name)
    connection_rule = assert_rule_is_deployed(github_connection_rule_name)
    assert connection_rule['order'] < hierarchy_rule['order']


def delete_rules_by_name(name):
    for client in filter(lambda c: c['name'] == name, AUTH0_CLIENT.rules.all()):
        AUTH0_CLIENT.rules.delete(client['id'])


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
    for client in clients_by_name(name):
        AUTH0_CLIENT.clients.delete(client['client_id'])


def clients_by_name(name):
    return list(filter(lambda c: c['name'] == name, AUTH0_CLIENT.clients.all()))


def delete_provider_by_name(name):
    client = boto3.client('iam')
    providers = providers_from_name(name, client)
    for p in providers:
        client.delete_saml_provider(
            SAMLProviderArn=p['Arn']
        )


def connections_by_name(name):
    return list(filter(lambda c: c['name'] == name, AUTH0_CLIENT.connections.all()))


def delete_connection_by_name(name):
    for connection in connections_by_name(name):
        AUTH0_CLIENT.connections.delete(connection['id'])


def assert_saml_is_configured(client):
    assert client['addons'] is not None
    assert client['addons']['samlp'] is not None
    assert client['addons']['samlp']['audience'] == 'https://signin.aws.amazon.com/saml'
    assert client['addons']['aws'] is not None


def assert_github_connection_is_configured(client):
    client_id = client['client_id']
    connections = list(
        filter(lambda conn: client_id in conn['enabled_clients'] and conn['name'] == github_connection_name,
               AUTH0_CLIENT.connections.all()))
    print("connections: " + str(connections))
    assert len(connections) == 1
    assert connections[0]['strategy'] == 'github'
    assert connections[0]['options']['profile'] == True
    assert connections[0]['options']['client_id'] == fake_github_id
    assert connections[0]['options']['client_secret'] == fake_github_secret

    assert connections[0]['name'] == github_connection_name
