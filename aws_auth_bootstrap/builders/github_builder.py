import requests


class GithubBuilder:
    def __init__(self, config):
        # TODO: validate required fields
        self.config = config

    def create_team(self, name, team_members_names):
        response = requests.post(f"https://api.github.com/orgs/{self.config['organization']}/teams",
                                 json={
                                     "name": name
                                 },
                                 headers={
                                     "Authorization": f"token {self.config['token']}"
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

    def add_member_to_team(self, team_id, member_name):
        response = requests.put(f"https://api.github.com/teams/{team_id}/memberships/{member_name} ",
                                headers={
                                    "Authorization": f"token {self.config['token']}"
                                }
                                )
        if response.status_code != 200:
            print(f"Error: {response.status_code} = {response.json()}")
            raise Exception("Failed to create team")
