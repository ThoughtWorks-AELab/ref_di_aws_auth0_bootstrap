import json

import os
import pkg_resources
import boto3
import urllib.request
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0

from aws_auth_bootstrap.builders.script_generator import ScriptGenerator

resource_package = __name__


def auth0_client_config():
    return {  # TODO: get rid of this thing
        "domain": os.environ['AUTH0_HOST'] + ".auth0.com",
        "client_id": os.environ['AUTH0_CLIENT_ID'],
        "client_secret": os.environ['AUTH0_CLIENT_SECRET']
    }


def create_auth0_client(config=auth0_client_config()):
    domain = config["domain"]
    token = GetToken(domain).client_credentials(config["client_id"],
                                                config["client_secret"], f"https://{domain}/api/v2/")
    return Auth0(domain, token['access_token'])


class Auth0Builder:
    def __init__(self, auth0_client=create_auth0_client(), script_generator=ScriptGenerator()):
        self.auth0_client = auth0_client
        self.script_generator = script_generator

    def create_aws_saml_client(self, client_name, account_id):
        matching_clients = list(filter(lambda c: c['name'] == client_name, self.auth0_client.clients.all()))
        create_client_request = json.loads(
            pkg_resources.resource_string(resource_package, 'resources/base-auth0-client-message.json'))
        create_client_request['name'] = client_name
        create_client_request['client_metadata'] = {
            "aws_account_number": account_id
        }

        if len(matching_clients) == 0:
            return self.auth0_client.clients.create(create_client_request)
        else:
            del (create_client_request['jwt_configuration']['secret_encoded'])
            return self.auth0_client.clients.update(matching_clients[0]['client_id'], create_client_request)

    def get_saml_metadata_document(self, auth0_host, client_id):
        # TODO: check return code
        return urllib.request.urlopen(f"https://{auth0_host}/samlp/metadata/{client_id}").read().decode("utf-8")

    def create_aws_saml_provider(self, client_id, name):
        saml_metadata_document = self.get_saml_metadata_document(auth0_client_config()['domain'], client_id)
        client = boto3.client('iam')
        matching_saml_providers = list(
            filter(lambda provider: provider["Arn"].endswith(name), client.list_saml_providers()['SAMLProviderList']))
        if len(matching_saml_providers) > 0:
            return client.update_saml_provider(
                SAMLProviderArn=matching_saml_providers[0]["Arn"],
                SAMLMetadataDocument=saml_metadata_document
            )
        else:
            return client.create_saml_provider(
                SAMLMetadataDocument=saml_metadata_document,
                Name=name)

    def configure_sso(self, client_name, account_id, github_client_id, github_client_secret):
        new_client = self.create_aws_saml_client(client_name, account_id)
        new_provider = self.create_aws_saml_provider(new_client['client_id'], "auth0-" + client_name)
        new_connection = self.create_github_connection(f"{client_name}-connection", new_client['client_id'],
                                                       github_client_id, github_client_secret)
        return {"client": new_client, "provider": new_provider, "connection": new_connection}

    def create_github_connection(self, connection_name, enabled_client, github_client_id, github_secret):

        create_connection_request = json.loads(
            pkg_resources.resource_string(resource_package, 'resources/base-github-connection-message.json'))
        create_connection_request['name'] = connection_name
        create_connection_request['enabled_clients'] = [enabled_client]
        create_connection_request['options']['client_id'] = github_client_id
        create_connection_request['options']['client_secret'] = github_secret

        connections = list(filter(lambda c: c['name'] == connection_name, self.auth0_client.connections.all()))
        if len(connections) > 0:
            del create_connection_request['strategy']
            del create_connection_request['name']
            print(f"Updated connection {connection_name}")
            return self.auth0_client.connections.update(connections[0]['id'], create_connection_request)
        else:
            print(f"Created connection {connection_name}")
            return self.auth0_client.connections.create(create_connection_request)

    def deploy_rules(self, client_name, config):
        self.deploy_rule_hierarchy(client_name, config)
        self.deploy_github_connection_rule(client_name)

    def deploy_rule_hierarchy(self, role_hierarchy_rule_name, config):
        self.deploy_or_overwrite_rule({
            "name": role_hierarchy_rule_name + "-hierarchy-rule",
            "script": self.script_generator.generate_hierarchy(config),
            "order": 2,
            "stage": "login_success"
        })

    def deploy_github_connection_rule(self, client_name):
        self.deploy_or_overwrite_rule({
            "name": client_name + "-github-rule",
            "script": pkg_resources.resource_string(resource_package, 'resources/github_connection.js').decode("utf-8"),
            "order": 1,
            "stage": "login_success"
        })

    def deploy_or_overwrite_rule(self, body):
        # TODO: bug - if there is already a rule with a given order,
        # TODO: it fails. Need to figure out how to handle that situation.
        rules = list(filter(lambda c: c['name'] == body['name'], self.auth0_client.rules.all()))
        if len(rules) == 0:
            self.auth0_client.rules.create(body)
        else:
            self.auth0_client.rules.update(rules[0]['id'], {
                "name": body['name'],
                "script": body['script'],
                "order": body['order']
            })
