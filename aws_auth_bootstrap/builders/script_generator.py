from functools import reduce


class ScriptGenerator:
    def __init__(self):
        pass

    # TODO: check client id
    # TODO: check protocol and if it's delegated, set the add on configuration
    def generate_hierarchy(self, config):
        return f"""
            function (user, context, callback) {{
                var roleMapping = {self.__generate_role_map(config)};
                var role = "";
                
                function hasRole(idpRole, user) {{
                    return user.app_metadata.roles.filter(function(userRole){{
                        return userRole == idpRole;
                    }}).length > 0;
                }}
                
                var samlProvider = "arn:aws:iam::" 
                    + context.clientMetadata.aws_account_number +
                    ":saml-provider/{config['saml_provider_name']}";
                
                for (var i=0; i < roleMapping.length && !role; i++) {{
                    if (hasRole(roleMapping[i].idpRole, user)) {{
                        role = roleMapping[i].awsRole(user);
                    }}
                }}
                user.awsRole = role + "," + samlProvider;
                
                if (!user.awsRole) {{
                    return callback("No role could be assigned. Please have your admin check mappings between aws role and github team.", user, context);
                }}
            
                user.awsRoleSession = user.nickname;
                context.samlConfiguration.mappings = {{
                    'https://aws.amazon.com/SAML/Attributes/Role': 'awsRole',
                    'https://aws.amazon.com/SAML/Attributes/RoleSessionName': 'awsRoleSession'
                }};

                
                if (context.protocol == 'delegation') {{
                    context.addonConfiguration = context.addonConfiguration || {{}};
                    context.addonConfiguration.aws = context.addonConfiguration.aws || {{}};
                    context.addonConfiguration.aws.principal = samlProvider;
                    context.addonConfiguration.aws.role = role;
                }}
                
                callback(null, user, context);
            }}
        """

    def __generate_role_mapping(self, role_tuple):
        aws_role_function = f"""
            function(user) {{
                return "arn:aws:iam::" +
                    context.clientMetadata.aws_account_number +
                    ":role/{role_tuple[1]}";
            }}
        """

        return f"""{{ idpRole:"{role_tuple[0]}", awsRole: {aws_role_function} }}"""

    def __generate_role_map(self, config):
        role_map = reduce(lambda acc, item: acc + ",\n" + item,
                          map(lambda role_tuple: self.__generate_role_mapping(role_tuple),
                              config['roles']))
        if config:
            return f"""[
                    {role_map}
            ]"""
        else:
            return f"[]"
