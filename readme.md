## Requirements
* virtualenv
* an auth0 account

## Assumptions
* Names are unique. This is not enforced by auth0, but we will overwrite
configuration with configuration if the name is used. If this is not
acceptable, this code will need to be changed to save state of the client ids

## Installation
* prepare the python environment

        virtualenv -p python3 .env

* create an auth0 [non-interactive client](https://auth0.com/docs/api/management/v2/tokens#1-create-a-client).
    You might have to [enable the APIs feature](https://manage.auth0.com/#/account/advanced)
    in your advanced settings.

    Makes sure to grant the following scopes to the client:
    * create:clients
    * read:clients
    * update:clients
    * delete:clients
    * create:rules
    * read:rules
    * update:rules
    * delete:rules
    * read:connections
    * update:connections
    * delete:connections

* create a [github oauth application](https://auth0.com/docs/connections/social/github)
for your personal or group account. You will need the client id and secret.

* create teams for each role you would like to support within AWS.
Current bootstrap supports dev_admin and infra_reader

* Create a file called .auth0 that only you can read that will set
environment variables:

        #.auth0
        export AUTH0_DOMAIN=myaccount.auth0.com
        export AUTH0_CLIENT_ID=exampleid
        export AUTH0_CLIENT_SECRET=********

        export PREPROD_AWS_ACCOUNT_NUMBER=0775854933855
        export PREPROD_AWS_ACCESS_ID=AKIAJRKDMHJTUJ48NOKFA
        export PREPROD_SECRET_ACCESS_KEY=********************

        export GITHUB_CLIENT_ID=d5kgjgji58124ifjgjfkc
        export GITHUB_CLIENT_SECRET=*************************

        chmod 700 .creds
        . .auth0

You will need to source this file prior to running the setup.

# Known Bugs and Issues
- CLI-based SSO is not yet enabled
- mapping main IAM account to other accounts

- bootstrap.py
    - better logging in scripts so you can see what actually occurs
    - validation for config structure so there are better error messages
    - fix need for multiple places saml provider is specified

- testing
    - fix tests for javascript to catch edge cases like no role assigned
    - clear users from auth0 before running tests and run a second time
    since there are two workflows

- misc
    - set up github teams from script
    - make testing require option explicit, if possible
    - refactor

- auth0tools.py
    - get rid of auth0_client_config function

- terraform:
    - parameterize the name of the saml provider
