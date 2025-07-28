from setuptools import setup, find_packages

setup(
    name='hubspot_s3_uploader',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'boto3',
        'gspread',
        'oauth2client',
        'requests',
        'python-dateutil'
    ],
    entry_points={
        'console_scripts': [
            'run-profile-etl=hubspot_s3_uploader.runner:main'
        ],
    },
    author='Jing Su',
    description='ETL pipeline for product profiles from S3 to HubSpot',
)
