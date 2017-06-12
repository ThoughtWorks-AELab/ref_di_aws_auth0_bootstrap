import json
import os
import challenge
import aws_creds
import socketserver
import requests
from urllib.parse import urlparse, parse_qs
from http.server import SimpleHTTPRequestHandler


UI_PORT = 8000
BACKEND_PORT = 8001

ENVIRONMENT = {
    "host": os.environ['AUTH0_HOST'] + ".auth0.com",
    "connection": "preproduction-connection",
    "client_id": os.environ['AUTH0_CLIENT_ID']
    }

def env():
    return json.dumps(ENVIRONMENT)

def token_exchange(code):
    params = {}
    params["code_verifier"] = challenge.generate()["verifier"]
    params["code"] = code
    params["redirect_uri"] = 'http://localhost:8000/code'
    params["client_id"] = ENVIRONMENT["client_id"]
    params["grant_type"] = "authorization_code"
    url = "https://{}/oauth/token".format(ENVIRONMENT["host"])
    request = requests.post(url, data=params)
    return request.json()

def aws_delegation(id_token):
    body = {}
    body["client_id"] = ENVIRONMENT["client_id"]
    body["target"] = ENVIRONMENT["client_id"]
    body["api_type"] = "aws"
    body["grant_type"] = "urn:ietf:params:oauth:grant-type:jwt-bearer"
    body["id_token"] = id_token
    url = "https://{}/delegation".format(ENVIRONMENT["host"])
    request = requests.post(url, data=body)
    return request.json()

class BackendHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # this space intentionally left blank
        return
    def do_GET(self):
        if self.path.startswith("/env"):
            response = bytearray(env(), "utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        if self.path.startswith("/callback"):
            response = bytearray(self.path, "utf-8")
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        elif self.path.startswith("/code"):
            auth_code = parse_qs(urlparse(self.path).query)['code'][0]
            token_resp = token_exchange(auth_code)
            id_token = token_resp["id_token"]
            resp = aws_delegation(id_token)
            creds = resp["Credentials"]
            aws_creds.update(creds)
            mystr = "You should be good to go. Try running `aws` commands with profile `auth0_federated`"
            response = bytearray(mystr, "utf-8")

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        else:
            super().do_GET()

def serve():
    with socketserver.TCPServer(("", UI_PORT), BackendHandler) as ui_server:
        ui_server.handle_request()
