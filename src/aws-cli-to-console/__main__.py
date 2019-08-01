import argparse
import cli_to_console


def main():

    parser = argparse.ArgumentParser(
        description="Choose an AWS profile from ~/.aws/config that you want to open in the web console."
    )

    parser.add_argument(
        '--profile-name',
        required=True,
        type=str,
        help="A name of a profile from ~/.aws/config"
    )

    args = vars(parser.parse_args())

    cli_to_console(args['profile_name'])


if __name__ == "__main__":
    main()