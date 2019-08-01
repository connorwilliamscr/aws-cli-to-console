import json
import sys
import urllib

import boto3  # AWS SDK for Python (Boto3) 'pip install boto3'
import requests  # 'pip install requests'
import configparser
import logging

logger = logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CliToConsole(self):
    def __init__(self, destination_profile):
        aws_config = configparser.ConfigParser()
        aws_config.read('/Users/connorwilliams/.aws/config')
        self.destination_profile = destination_profile

    def create_signed_url(self):
        profile_order = self._build_switchrole_order(self.destination_profile)


    def _build_switchrole_order(destination_profile):
        """Builds an ordered list of profile names ready to assume the roles in order"""
        section_name = 'profile ' + destination_profile
        profiles = [destination_profile]
        if 'source_profile' in aws_config[section_name]:
            source_profile = aws_config[section_name]['source_profile']
            profiles = build_switchrole_order(source_profile) + profiles
        return profiles



session = boto3.session.Session(
    profile_name=profile_order.pop(0)
)

for profile_name in profile_order:
    section_name = 'profile ' + profile_name
    session = boto3.session.Session(profile_name=profile_name)
    sts_connection = session.client(
        'sts',
        aws_access_key_id=assumed_role_object.get('AccessKeyId', None),
        aws_secret_access_key=assumed_role_object.get('SecretAccessKey', None),
        aws_session_token=assumed_role_object.get('SessionToken', None)
    )
    assumed_role_object = sts_connection.assume_role(
        RoleArn=aws_config[section_name]['role_arn'],
        RoleSessionName="AssumeRoleSession",
    )

# Step 1: Authenticate user in your own identity system.

# Step 2: Using the access keys for an IAM user in your AWS account,
# call "AssumeRole" to get temporary access keys for the federated user

# # Step 3: Format resulting temporary credentials into JSON
url_credentials = {}
url_credentials['sessionId'] = assumed_role_object.get('Credentials').get('AccessKeyId')
url_credentials['sessionKey'] = assumed_role_object.get('Credentials').get('SecretAccessKey')
url_credentials['sessionToken'] = assumed_role_object.get('Credentials').get('SessionToken')
json_string_with_temp_credentials = json.dumps(url_credentials)

# Step 4. Make request to AWS federation endpoint to get sign-in token. Construct the parameter string with
# the sign-in action request, a 12-hour session duration, and the JSON document with temporary credentials 
# as parameters.
request_parameters = "?Action=getSigninToken"
if sys.version_info[0] < 3:
    def quote_plus_function(s):
        return urllib.quote_plus(s)
else:
    def quote_plus_function(s):
        return urllib.parse.quote_plus(s)
request_parameters += "&Session=" + quote_plus_function(json_string_with_temp_credentials)
request_url = "https://signin.aws.amazon.com/federation" + request_parameters
r = requests.get(request_url)
# Returns a JSON document with a single element named SigninToken.
signin_token = json.loads(r.text)

# Step 5: Create URL where users can use the sign-in token to sign in to 
# the console. This URL must be used within 15 minutes after the
# sign-in token was issued.
request_parameters = "?Action=login" 
request_parameters += "&Issuer=Example.org" 
request_parameters += "&Destination=" + quote_plus_function("https://console.aws.amazon.com/")
request_parameters += "&SigninToken=" + signin_token["SigninToken"]
request_url = "https://signin.aws.amazon.com/federation" + request_parameters

# Send final URL to stdout
print (request_url)