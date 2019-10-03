import argparse
import getpass

USER_NAME = getpass.getuser()


def get_arguments(args):
    """
    Defines and returns input arguments
    :return: argparse.Namespace object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--profile',
        help='Name of a profile in your awscli config file that you want to sign in to the console with',
        required=True
    )
    default_aws_dir_path = f'/Users/{USER_NAME}/.aws/'
    parser.add_argument(
        '--config',
        action='store_true',
        help=f"File path to your awscli config file. Defaults to {default_aws_dir_path+'config'}",
        default=default_aws_dir_path+'config'
    )
    parser.add_argument(
        '--credentials',
        action='store_true',
        help=f"File path to your awscli config file. Defaults to {default_aws_dir_path+'credentials'}",
        default=default_aws_dir_path+'credentials'
    )
    return parser.parse_args()