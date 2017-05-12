## Requirements
* virtualenv
* an auth0 account

## Assumptions
* Names are unique. This is not enforced by auth0, but we will overwrite configuration with
configuration if the name is used. If this is not acceptable, this code will need to be changed to save
state of the client ids

## Installation
* prepare the python environment

        virtualenv -p python3 .env

* create an auth0 [non-interactive client](https://auth0.com/docs/api/management/v2/tokens#1-create-a-client).
    You might have to [enable the APIs feature](https://manage.auth0.com/#/account/advanced) in your advanced settings.
    Makes sure to grant the following scopes to the client:
    * create:clients
    * read:clients
    * update:clients
    * delete:clients
    * create:rules
    * read:rules
    * update:rules
    * delete:rules

* Create a file called .auth0 that only you can read that will set environment variables:

        #.auth0
        export AUTH0_DOMAIN=myaccount.auth0.com
        export AUTH0_CLIENT_ID=exampleid
        export AUTH0_CLIENT_SECRET=********
        export AWS_ACCESS_KEY_ID=AKIAJRKDMHJTUJ48NOKFA
        export AWS_SECRET_ACCESS_KEY=********************

        chmod 700 .creds
        . .auth0

You will need to source this file prior to running the setup.

