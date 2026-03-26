from setuptools import setup

setup(
    name='downloader',
    version='0.1.0',
    packages=['downloader'],
    install_requires=[
        'fastapi>=0.104.0',
        'uvicorn[standard]>=0.24.0',
        'pydantic>=2.0.0',
        'pydantic-settings>=2.0.0',
    ],
)