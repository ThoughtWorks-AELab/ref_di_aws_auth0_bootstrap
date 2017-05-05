## Requirements
* virtualenv
* an auth0 account

## Installation
* prepare the python environment

        virtualenv -p python3 .env
        pip install -r requirements.txt

* create an auth0 [non-interactive client](https://auth0.com/docs/api/management/v2/tokens#1-create-a-client).
    You might have to [enable the APIs feature](https://manage.auth0.com/#/account/advanced) in your advanced settings.
    Makes sure to grant the following scopes to the client:
    * create:clients
    * read:clients
    * update:clients
    * delete:clients

* Create a file called .auth0 that only you can read that will set environment variables for DOMAIN, CLIENT_ID, and CLIENT_SECRET. For example:

        #.auth0
        export AUTH0_DOMAIN=myaccount.auth0.com
        export AUTH0_CLIENT_ID=exampleid
        export AUTH0_CLIENT_SECRET=examplesecret

        chmod 700 .creds
        . .auth0

You will need to source this file prior to running the setup.

