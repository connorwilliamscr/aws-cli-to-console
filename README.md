A tool which builds a signed URL for AWS console login for any profile in your `~/.aws/config`

* Only works on unix based systems

## Installation

`pip install git+https://github.com/connorwilliamscr/aws-cli-to-console.git`

## Prerequisites
* [Set up profile in `~/.aws/config`](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) (See examples below)

## Usage

`python aws-cli-to-console --profile profilename`

Get help with `python aws-cli-to-console --help`


## AWS CLI Config Examples

#### Normal AWS CLI profile

```
[profile root-account]
aws_access_key_id = AKAKAKAKAKAKAKA432524
aws_secret_access_key = lknQLkjfslknDUDHUI73enfJNkfsidofheDN
region = eu-west-1
```


#### [Role Chaining](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_terms-and-concepts.html#iam-term-role-chaining)

When you use a role to assume a second role. Notice in the example aws cli config file below that the role chain goes `root-account` -> `sub-account` -> `sub-sub-account` (from looking at the `source_profile`s). You may have something like this if you are using AWS Organizations.

```
[profile root-account]
aws_access_key_id = AKAKAKAKAKAKAKA432524
aws_secret_access_key = lknQLkjfslknDUDHUI73enfJNkfsidofheDN
region = eu-west-1

[profile sub-account]
source_profile = root-account
role_arn = arn:aws:iam::123456789:role/role_name
region = eu-west-1

[profile sub-sub-account]
source_profile = sub-account
role_arn = arn:aws:iam::987654321:role/role_name
region = eu-west-1
```