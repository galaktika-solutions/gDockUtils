from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

VERSION = '0.3.2'

setup(
    name='gdockutils',
    description='Galaktika Solutions - Docker Utilities',
    long_description=long_description,
    version=VERSION,
    url='https://github.com/galaktika-solutions/gDockUtils',
    author='Richard Bann',
    author_email='richardbann@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ],
    license='MIT',
    packages=['gdockutils'],
    install_requires=[
        'pyyaml >= 3.13',
    ],
    entry_points={
        'console_scripts': [
            'gprun=gdockutils.gprun:gprun_cli',
            'ask=gdockutils.ui:ask_cli',
            'createsecret=gdockutils.secret:createsecret_cli',
            'createsecret_ui=gdockutils.ui:createsecret_ui',
            'readsecret=gdockutils.secret:readsecret_cli',
            'readsecret_ui=gdockutils.ui:readsecret_ui',
            'ensure_db=gdockutils.db:ensure_db_cli',
            'backup=gdockutils.db:backup_cli',
            'backup_ui=gdockutils.ui:backup_ui',
            'restore=gdockutils.db:restore_cli',
            'restore_ui=gdockutils.ui:restore_ui',
            'prepare=gdockutils.prepare:prepare_cli',
            'createcerts=gdockutils.certificates:create_cli'
        ],
    }
)
