Script for managing inactive users in Slack
Intended for non-paid teams (I assume paid teams get better tools), but if a 
paid team finds something useful about it feel free, it is under the MIT License

Goes through all the messages in a Slack team and finds all users that have not 
commented, in the case of non-paid teams that's only for the last ten thousand 
messages. It can either just list all users and the number of days since they 
spoke, or you can have it remove all non-speaking users from all public channels

Note, you need to include a slack admin user token which you can get at 
https://api.slack.com/docs/oauth-test-tokens, just pick one for the team you 
want to manage and add it to slack_token at the beginning fo the file