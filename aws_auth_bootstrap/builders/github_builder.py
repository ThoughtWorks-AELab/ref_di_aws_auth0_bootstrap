import requests


class GithubBuilder:
    def __init__(self, config):
        # TODO: validate required fields
        self.config = config

    def create_team(self, team_name, team_members_names):
        organization_name = self.config['github_organization']
        if not self.__team_exists(organization_name, team_name):
            print(f"Creating team {team_name}")
            response = requests.post(f"https://api.github.com/orgs/{organization_name}/teams",
                                     json={
                                         "name": team_name
                                     },
                                     headers={
                                         "Authorization": f"token {self.config['github_automation_token']}"
                                     }
                                     )
            if response.status_code != 201:
                print(f"Error: {response.status_code} = {response.json()}")
                raise Exception("Failed to create team")
            else:
                response_json = response.json()
                for member_name in team_members_names:
                    self.add_member_to_team(response_json['id'], member_name)
                return response_json
        else:
            print(f"Team {team_name} already exists.")

    def add_member_to_team(self, team_id, member_name):
        response = requests.put(f"https://api.github.com/teams/{team_id}/memberships/{member_name} ",
                                headers={
                                    "Authorization": f"token {self.config['github_automation_token']}"
                                }
                                )
        if response.status_code != 200:
            print(f"Error: {response.status_code} = {response.json()}")
            raise Exception("Failed to create team")

    def __team_exists(self, organization_name, team_name):
        return len(list(filter(lambda team: team['name'] == team_name,
                               requests.get(f"https://api.github.com/orgs/{organization_name}/teams", headers={
                                   "Authorization": f"token {self.config['github_automation_token']}"}).json()))) == 1
