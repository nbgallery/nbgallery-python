from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nbgallery',
    version='0.0.1',
    description='Python interface to local nbgallery',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nbgallery/nbgallery-python',
    author='https://github.com/nbgallery',
    license='MIT',
    packages=['nbgallery'],
    install_requires=[
        'appdirs',
        'inflect',
        'mysqlclient',
        'nbformat',
        'nbstripout',
        'pandas',
        'ruamel.yaml',
        'SQLAlchemy',
        'sqlalchemy-mixins',
        'SQLAlchemy-Utils'
    ]
)
