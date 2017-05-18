import os
from time import time

import requests

from aws_auth_bootstrap.builders.github_builder import GithubBuilder

ORG_NAME = "thoughtworks-dps-testing"
TEAM_NAME = 'team' + str(int(time() * 1000))
TOKEN = os.environ['GITHUB_TEST_USER_TOKEN']
MEMBER_NAME = 'thoughtworks-dps-machine-account-2'


def teardown_function(fn):
    delete_team(ORG_NAME, TEAM_NAME)


def test_build_teams():
    config = {
        "token": TOKEN,
        "organization": ORG_NAME
    }

    GithubBuilder(config).create_team(TEAM_NAME, {
        MEMBER_NAME
    })

    validate_team_exists(ORG_NAME, TEAM_NAME)
    validate_member_is_in_team(ORG_NAME, TEAM_NAME, MEMBER_NAME)


def delete_team(organization_name, team_name):
    teams = get_teams_by_name(organization_name, team_name)
    for team in teams:
        requests.delete(f"https://api.github.com/teams/{team['id']}",
                        headers={"Authorization": f"token {TOKEN}"})


def get_teams_by_name(organization_name, team_name):
    return filter(lambda team: team['name'] == team_name,
                  requests.get(f"https://api.github.com/orgs/{organization_name}/teams",
                               headers={"Authorization": f"token {TOKEN}"}).json())


def validate_team_exists(organization_name, team_name):
    response = requests.get(f"https://api.github.com/orgs/{organization_name}/teams",
                            headers={"Authorization": f"token {TOKEN}"})
    assert response.status_code == 200
    teams = list(filter(lambda team: team['name'] == team_name,
                        response.json()))
    assert len(teams) == 1


def validate_member_is_in_team(organization_name, team_name, member_name):
    teams = list(get_teams_by_name(organization_name, team_name))
    assert len(teams) == 1
    response = requests.get(f"https://api.github.com/teams/{teams[0]['id']}/memberships/{member_name}",
                            headers={"Authorization": f"token {TOKEN}"})
    assert response.status_code == 200
    assert response.json()['state'] == 'active'
