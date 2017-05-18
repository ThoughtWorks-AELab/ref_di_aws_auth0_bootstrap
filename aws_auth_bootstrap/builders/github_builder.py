import requests


class GithubBuilder:
    def __init__(self, config):
        # TODO: validate required fields
        self.config = config

    def create_team(self, name, team_members):
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
            return response.json
