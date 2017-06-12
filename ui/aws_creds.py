import configparser
from os.path import expanduser

def update(creds):
    filepath = expanduser('~/.aws/credentials')
    config = configparser.ConfigParser()
    config.read(filepath)
    if not config.has_section('auth0_federated'):
        config.add_section('auth0_federated')

    profile = config['auth0_federated']
    profile['aws_access_key_id'] = creds['AccessKeyId']
    profile['aws_secret_access_key'] = creds['SecretAccessKey']
    profile['aws_session_token'] = creds['SessionToken']

    with open(filepath, 'w+') as output_file:
        config.write(output_file)
