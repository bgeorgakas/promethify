from setuptools import setup

setup(
    name='db',
    version='0.1.0',
    packages=['db'],
    install_requires=[
        'sqlalchemy>=2.0.0,<3.0.0',
        'psycopg2-binary>=2.9.0,<3.0.0',
    ],
)