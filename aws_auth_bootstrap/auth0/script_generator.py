from functools import reduce


class ScriptGenerator:
    def __init__(self):
        pass

    def generate_role_mapping(self, role_tuple, saml_provider):
        aws_role_function = f"""
            function(user) {{
                return "arn:aws:iam::" +
                    context.clientMetadata.aws_account_number +
                    ":role/{role_tuple[1]},arn:aws:iam::" +
                    context.clientMetadata.aws_account_number +
                    ":saml-provider/{saml_provider}"
            }}
        """

        return f"""{{ idpRole:"{role_tuple[0]}", awsRole: {aws_role_function} }}"""

    def generate_role_map(self, config):
        role_map = reduce(lambda acc, item: acc + ",\n" + item,
                          map(lambda role_tuple: self.generate_role_mapping(role_tuple, config['saml_provider_name']),
                              config['roles']))
        if config:
            return f"""[
                    {role_map}
            ]"""
        else:
            return f"[]"

    def generate_hierarchy(self, config):
        return f"""
            function (user, context, callback) {{
                roleMapping = {self.generate_role_map(config)};
                
                function hasRole(idpRole, user) {{
                    return user.app_metadata.roles.filter(function(mapping){{
                        return mapping.idpRole = idpRole;
                    }}).length > 0;
                }}
                
                for (i=0; i < roleMapping.length && !user.awsRole; i++) {{
                    if (hasRole(roleMapping[i].idpRole, user)) {{
                        user.awsRole = roleMapping[i].awsRole(user);
                    }}
                }}
            
                user.awsRoleSession = user.nickname;
                context.samlConfiguration.mappings = {{
                    'https://aws.amazon.com/SAML/Attributes/Role': 'awsRole',
                    'https://aws.amazon.com/SAML/Attributes/RoleSessionName': 'awsRoleSession'
                }};
                callback(null, user, context);
            }}
        """
