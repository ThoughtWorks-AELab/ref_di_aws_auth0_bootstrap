from setuptools import setup, find_packages

setup(
    name='aws-auth-bootstrap',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=True,
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
