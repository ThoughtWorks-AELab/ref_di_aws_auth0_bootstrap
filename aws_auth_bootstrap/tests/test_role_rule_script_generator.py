import json

import execjs

from aws_auth_bootstrap.builders.role_rule_script_generator import RoleRuleScriptGenerator


def run_test_script(script, user, context):
    user_json = json.dumps(user)
    context_json = json.dumps(context)

    test_script = f"""
        function test() {{
            fn = {script};
            result = {{ }};
            context = JSON.parse('{context_json}')
            user = JSON.parse('{user_json}')
            
            fn(user, context, function(returnError, returnUser, returnContext){{
                result.error = returnError;
                result.user = returnUser;
                result.context = returnContext
            }})
            return result;
        }}
    """
    print("####### THE SCRIPT #############")
    print(test_script)
    print("####### END OF THE SCRIPT #############")
    return execjs.compile(test_script).call("test")


script = RoleRuleScriptGenerator().generate_hierarchy({
    "client_ids": ["qwer1234"],
    "saml_provider_name": "zaml",
    "roles": [
        {
            "idp_role": "git-group/github-role-1",
            "aws_role": "aws-role-1"
        },
        {
            "idp_role": "git-group/github-role-2",
            "aws_role": "aws-role-2"
        }
    ]
})


def test_generate_hierarchy_script_from_mapping():
    result = run_test_script(script, user={
        "app_metadata": {
            "roles": ['git-group/github-role-1']
        },
        "nickname": 'bob'
    }, context={
        "clientID": "qwer1234",
        "clientMetadata": {"aws_account_number": '1234'},
        "samlConfiguration": {}
    })

    assert result["error"] is None
    assert "user" in result
    assert "awsRole" in result["user"]
    print(result["user"]["awsRole"])
    assert result["user"]["awsRole"] == 'arn:aws:iam::1234:role/aws-role-1,arn:aws:iam::1234:saml-provider/zaml'


def test_script_does_not_map_roles_for_nonmatching_client_id():
    user = {"app_metadata": {"roles": ['git-group/github-role-1']}, "nickname": 'bob'}
    context = {"clientID": "nonmatching1234", "clientMetadata": {"aws_account_number": '1234'},
                      "samlConfiguration": {}}
    result = run_test_script(script, user=user, context=context)

    # Check that nothing was changed because logic never ran
    assert result["error"] is None
    assert result["user"] == user
    assert result["context"] == context
