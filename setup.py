import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aws-cli-to-console",
    version="1.0.0",
    author="Connor Williams",
    author_email="connor.williams@cloudreach.com",
    description="A tool which generates a URL for the AWS console",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/connorwilliamscr/aws-cli-to-console.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'aws-cli-to-console = cli_to_console.cli_to_console:cli'
        ]
    }
)