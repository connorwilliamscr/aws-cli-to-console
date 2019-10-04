import configparser
import json
import logging
import sys
import urllib

import boto3
import botocore
import requests

import cli_to_console.argparser as argparser

logger = logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AwsCliProfileAssumeRole:
    """
    Assumes any role in your aws cli config
    """

    def __init__(self, config_path, credentials_path, destination_profile):
        self.aws_config = configparser.ConfigParser()
        self.aws_config.read(config_path)
        self.aws_credentials = configparser.ConfigParser()
        self.aws_credentials.read(credentials_path)
        self.ordered_profiles = self.order_profiles(destination_profile)
        logger.debug(f"Profiles in role chaining order are {self.ordered_profiles}")
        self.credentials = self.chain_roles()
    
    def order_profiles(self, destination_profile):
        """
        Recursively creates a list of aws profile names from awscli config file
        in order of roles to assume to get to the desired profile
        """
        section_name = 'profile ' + destination_profile
        profiles = [destination_profile]
        if 'source_profile' in self.aws_config[section_name]:
            source_profile = self.aws_config[section_name]['source_profile']
            profiles = self.order_profiles(source_profile) + profiles
        return profiles
    
    def chain_roles(self):
        """
        Traverses the list of ordered profiles and assumes roles down the chain
        Returns the credentials from boto3 sts.assume_role
        """
        # Start with the top most profile's credentials
        root_profile_name = self.ordered_profiles.pop(0)
        sts_connection, credentials = self.get_root_profile_credentials(root_profile_name)        

        # Loop through rest of profiles and assume roles down the chain
        for profile_name in self.ordered_profiles:
            section_name = 'profile ' + profile_name
            logger.debug(f"Assuming role for {section_name}")
            # Assume the role, start a new session and sts connection with it
            credentials = sts_connection.assume_role(
                RoleArn=self.aws_config[section_name]['role_arn'],
                RoleSessionName="AssumeRoleSession",
            )['Credentials']
            session = boto3.session.Session(profile_name=profile_name)
            sts_connection = session.client(
                'sts',
                aws_access_key_id=credentials.get('AccessKeyId', None),
                aws_secret_access_key=credentials.get('SecretAccessKey', None),
                aws_session_token=credentials.get('SessionToken', None)
            )
        
        return credentials
    
    def get_root_profile_credentials(self, root_profile_name):
        """
        Get the credentials of the first profile in the chain of assume roles.
        This can be from an IAM user sessions, federated user sessions, or from AWS credentials file.
        """
        session = boto3.session.Session(
            profile_name=root_profile_name
        )
        sts_connection = session.client('sts')
        # Multiple try/excepts like this because we are catching the same type of exception twice in a row
        try:
            logger.error("Getting creds with session token...")
            credentials = sts_connection.get_session_token()['Credentials']
            return sts_connection, credentials
        except botocore.exceptions.ClientError as e:
            logger.error(e)
        try:
            logger.info("Getting creds with federation token...")
            credentials = sts_connection.get_federation_token(
                Name='NAMEOFPERSON'
            )['Credentials']  
            return sts_connection, credentials
        except botocore.exceptions.ClientError as e:
            logger.error(e)
        try:
            logger.info("Getting creds from awscli credentials file...")
            credentials = {
                'AccessKeyId': self.aws_credentials[root_profile_name]['aws_access_key_id'],
                'SecretAccessKey': self.aws_credentials[root_profile_name]['aws_secret_access_key'],
                'SessionToken': self.aws_credentials[root_profile_name]['aws_session_token']
            }
            return sts_connection, credentials
        except:
            logger.error("Could not get credentials for top most profile in the chain.")
            raise


def build_federation_request_url(credentials):
    """
    Creates URL using the temporary credentials which will call
    the AWS federation endpoint to request a sign-in token.
    """
    # Format temporary credentials into JSON
    temp_credentials = {}
    temp_credentials['sessionId'] = credentials.get('AccessKeyId')
    temp_credentials['sessionKey'] = credentials.get('SecretAccessKey')
    temp_credentials['sessionToken'] = credentials.get('SessionToken')
    json_temp_credentials = json.dumps(temp_credentials)

    # Construct the parameter string with the sign-in action request
    # and the JSON document with temporary credentials as parameters.
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&Session=" + urllib.parse.quote_plus(json_temp_credentials)
    federation_url = "https://signin.aws.amazon.com/federation" + request_parameters
    logger.debug(f"Federation URL is: {federation_url}")
    return federation_url


def build_aws_console_url(signin_token):
    """
        Creates URL using the sign-in token which will sign the user in to the console.
    """
    request_parameters = "?Action=login" 
    request_parameters += "&Issuer=Example.org" 
    request_parameters += "&Destination=" + urllib.parse.quote_plus("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    console_url = "https://signin.aws.amazon.com/federation" + request_parameters
    logger.debug(f"Console URL is: {console_url}")
    return console_url


def main(args):    
    # Assume desired role and get credentials
    credentials = AwsCliProfileAssumeRole(
        config_path=args.config,
        credentials_path=args.credentials,
        destination_profile=args.profile
    ).credentials

    # Call AWS federation endpoint to get a sign-in token for the assumed role
    federation_request_url = build_federation_request_url(credentials)    
    response = requests.get(federation_request_url)
    signin_token = json.loads(response.text)

    console_url = build_aws_console_url(signin_token)
    logger.info(f"Your AWS Console link is: {console_url}")


if __name__ == '__main__':
    main(argparser.get_arguments(sys.argv[1:]))

def cli():
    main(argparser.get_arguments(sys.argv[1:]))
