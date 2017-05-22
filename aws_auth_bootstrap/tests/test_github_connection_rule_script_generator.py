import json

import execjs
import pkg_resources

from aws_auth_bootstrap.builders.github_connection_rules_script_generator import GithubConnectionRuleScriptGenerator

resource_package = __name__


def run_test_script(script, user, context):
    user_json = json.dumps(user)
    context_json = json.dumps(context)

    injections = str(pkg_resources.resource_string(resource_package, 'resources/mocks.js'), "utf=8")
    test_script = f"""
        
        function test() {{
        
            {injections}
        
            fn = {script};
            result = {{ }};
            context = JSON.parse('{context_json}')
            user = JSON.parse('{user_json}')
            
            fn(user, context, function(returnError, returnUser, returnContext){{
                result.error = returnError;
                result.user = returnUser;
                result.context = returnContext
                result.metaDataUpdate = metaDataUpdate;
            }})
            return result;
        }}
    """
    return execjs.compile(test_script).call("test")


def test_generate_policy_from_mapping():
    script = GithubConnectionRuleScriptGenerator().generate({
        "user_agent": "my client name"
    })

    result = run_test_script(script, user={
        "user_id": "the-user-id",
        "identities": [
            {
                "provider": "github",
                "access_token": "the-access-token"
            }
        ]
    }, context={})

    print(result)
    assert result["error"] is None
    assert result["user"]["app_metadata"]["roles"] == ["organization-name/team-name"]
    assert result["metaDataUpdate"]["userId"] == "the-user-id"
    assert result["metaDataUpdate"]["appMetaData"]["roles"] == ["organization-name/team-name"]
