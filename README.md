A tool which builds a signed URL for AWS console login for any profile in your ~/.aws/config

Only works on unix based systems

## Installation

`pip install `

## Prerequisites

### Set up profile in `~/.aws/config`

#### Normal profile

*Example of normal profile*


#### [Role Chaining](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_terms-and-concepts.html#iam-term-role-chaining)

When you use a role to assume a second role.

*Example of role chaining from aws config file (source_profile)*

## Usage

*Paste output from help command*

Get help with `python cli-to-console --help`

Get URL to console for any profile in `~/.aws/config` with `python cli-to-console --profile profilename`