import webbrowser
from urllib.parse import urlencode
import os
import challenge

auth0_host = os.environ['AUTH0_HOST'] + '.auth0.com'
client_id = os.environ['AUTH0_CLIENT_ID']
connection = 'preproduction-connection'
callback_host = 'localhost'
callback_port = 8000

base_url = "https://{}/authorize".format(auth0_host)

def initiate_sso():

    params = {}
    params['scope'] = 'openid name email nickname'
    params['response_type'] = 'code'
    params['state'] = 'TODO'
    params['sso'] = True
    params['connection'] = connection
    params['client_id'] = client_id
    params['code_challenge'] = challenge.generate()["challenge"]
    params['code_challenge_method'] = 'S256'
    params['redirect_uri'] = 'http://{}:{}/code'.format(callback_host, callback_port)

    auth_url = "{}?{}".format(base_url, urlencode(params))

    webbrowser.open(auth_url)



