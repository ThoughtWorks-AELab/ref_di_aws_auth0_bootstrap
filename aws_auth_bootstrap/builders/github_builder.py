import requests


class GithubBuilder:
    def __init__(self, config):
        self.github_organization = config['github_organization']
        self.github_automation_token = config['github_automation_token']

    def create_team(self, team_name, team_members_names):
        if not self.__team_exists(self.github_organization, team_name):
            print(f"Creating team {team_name}")
            response = requests.post(f"https://api.github.com/orgs/{self.github_organization}/teams",
                                     json={
                                         "name": team_name
                                     },
                                     headers={
                                         "Authorization": f"token {self.github_automation_token}"
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
                                    "Authorization": f"token {self.github_automation_token}"
                                }
                                )
        if response.status_code != 200:
            print(f"Error: {response.status_code} = {response.json()}")
            raise Exception("Failed to create team")

    def __team_exists(self, organization_name, team_name):
        return len(list(filter(lambda team: team['name'] == team_name,
                               requests.get(f"https://api.github.com/orgs/{organization_name}/teams", headers={
                                   "Authorization": f"token {self.github_automation_token}"}).json()))) == 1
