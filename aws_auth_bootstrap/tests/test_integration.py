from time import time

import boto3
import pytest

from aws_auth_bootstrap.auth0.auth0tools import configure_sso, create_auth0_client, Auth0Builder

client_name = 'testaccount' + str(int(time() * 1000))
account_id = "123-123-123"
saml_provider_name = "auth0-" + client_name
role_hierarchy_rule_name = client_name + "-rule-hierarchy"


def teardown_function(fn):
    delete_client_by_name(client_name)
    delete_provider_by_name(saml_provider_name)
    delete_rules_by_name(role_hierarchy_rule_name)


def test_configure_sso():
    created = configure_sso(client_name, account_id)
    assert_saml_is_configured(created['client'])
    assert_aws_provider_is_configured(saml_provider_name)


# def test_deploy_rules():
#     Auth0Builder().deploy_rule_hierarchy(role_hierarchy_rule_name, 2,
#                                   {
#                                       "account": account_id,
#                                       "saml_provider": saml_provider_name,
#                                       "roles": [
#                                           ("auth0-role-1", "aws-role-1"),
#                                           ("auth0-role-2", "aws-role-2")
#                                       ]
#                                   })
#     assert_rules_are_deployed()


#
# Utility methods
#
def assert_rule_is_deployed(name, auth0_client=create_auth0_client()):
    assert len(list(filter(lambda c: c['name'] == name, auth0_client.rules.all()))) == 1


def assert_rules_are_deployed():
    assert_rule_is_deployed(role_hierarchy_rule_name)


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
