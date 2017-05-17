import json
import execjs

from aws_auth_bootstrap.builders.script_generator import ScriptGenerator


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
    return execjs.compile(test_script).call("test")


def test_generate_policy_from_mapping():
    script = ScriptGenerator().generate_hierarchy({
        "saml_provider_name": "zaml",
        "roles": [
            ("org_name/auth0-role-1", "aws-role-1"),
            ("org_name/auth0-role-2", "aws-role-2")
        ]
    })

    result = run_test_script(script, user={
        "app_metadata": {
            "roles": ['org_name/auth0-role-1']
        },
        "nickname": 'bob'
    }, context={
        "clientMetadata": {"aws_account_number": '1234'},
        "samlConfiguration": {}
    })

    assert result["error"] is None
    assert "user" in result
    assert "awsRole" in result["user"]
    print(result["user"]["awsRole"])
    assert result["user"]["awsRole"] == 'arn:aws:iam::1234:role/aws-role-1,arn:aws:iam::1234:saml-provider/zaml'
