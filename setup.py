from setuptools import setup

setup(
    name='aws-auth-bootstrap',
    packages=['aws_auth_bootstrap'],
    include_package_data=False,
    install_requires=[
        'auth0-python==3.0.0',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'boto==2.46.1'
    ],
)