
var request = {
    get: function(config, callback) {
        if (
            config.url == 'https://api.github.com/user/teams' &&
            config.headers &&
            config.headers["Authorization"] == "token the-access-token" &&
            config.headers["User-Agent"] == "my client name"
            ) {
            callback(null, null, JSON.stringify([
                {
                    organization: {
                        login: "organization-name"
                    },
                    slug: "team-name"
                }
            ]));
        }
    }
};

var metaDataUpdate = {
    userId: null,
    appMetaData: null
}

var auth0 = {
    users: {
        updateAppMetadata : function(userId, appMetaData){
            metaDataUpdate.userId = userId;
            metaDataUpdate.appMetaData = appMetaData;
            return {
                then: function(fn){
                    fn();
                    return {
                        catch: function(){}
                    }
                }
            }
        }
    }
};