import os
from time import time

import requests

from aws_auth_bootstrap.builders.github_builder import GithubBuilder

ORG_NAME = "thoughtworks-dps-testing"
TEAM_NAME = 'team' + str(int(time() * 1000))
TOKEN = os.environ['GITHUB_TEST_USER_TOKEN']


def teardown_function(fn):
    delete_team(ORG_NAME, TEAM_NAME)


def test_build_teams():
    member_name = 'danielsomerfield'
    config = {
        "token": TOKEN,
        "organization": ORG_NAME
    }

    GithubBuilder(config).create_team(TEAM_NAME, {
        member_name
    })

    validate_team_exists(ORG_NAME, TEAM_NAME)
    validate_member_is_in_team(TEAM_NAME, member_name)


def delete_team(organization_name, team_name):
    teams = filter(lambda team: team['name'] == team_name,
                   requests.get(f"https://api.github.com/orgs/{organization_name}/teams",
                                headers={"Authorization": f"token {TOKEN}"}).json())
    for team in teams:
        requests.delete(f"https://api.github.com/teams/{team['id']}",
                        headers={"Authorization": f"token {TOKEN}"})


def validate_team_exists(organization_name, team_name):
    response = requests.get(f"https://api.github.com/orgs/{organization_name}/teams", headers={"Authorization": f"token {TOKEN}"})
    assert response.status_code == 200
    teams = list(filter(lambda team: team['name'] == team_name,
                        response.json()))
    assert len(teams) == 1


def validate_member_is_in_team(team_name, member_name):
    pass
