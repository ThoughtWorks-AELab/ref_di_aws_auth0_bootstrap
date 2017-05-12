from setuptools import setup

setup(
    name='aws-auth-bootstrap',
    packages=['aws_auth_bootstrap', 'aws_auth_bootstrap/builders'],
    include_package_data=False,
    install_requires=[
        'auth0-python==3.0.0',
        'boto3==1.4.4'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)