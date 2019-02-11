from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

VERSION = '0.5.16'

setup(
    name='gdockutils',
    description='Galaktika Solutions - Docker Utilities',
    long_description=long_description,
    long_description_content_type="text/markdown",
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
        'click >= 7.0',
    ],
    extras_require={
        "dev": [
            "coverage >= 4.5.2",
            "sphinx >= 1.8.4",
            "sphinx_rtd_theme >= 0.4.2",
            "twine >= 1.12.1",
            "wheel >= 0.32.3",
        ],
    },
    entry_points={
        'console_scripts': [
            'gstack=gdockutils.main:cli',
            # 'ensure_db=gdockutils.cli:ensure_db',
            # 'backup=gdockutils.cli:backup',
            # 'restore=gdockutils.cli:restore',
            # 'createsecret=gdockutils.cli:createsecret',
            # 'readsecret=gdockutils.cli:readsecret',
            # 'prepare=gdockutils.cli:prepare',
            # 'createsecret_ui=gdockutils.ui:createsecret_ui',
            # 'readsecret_ui=gdockutils.ui:readsecret_ui',
            # 'backup_ui=gdockutils.ui:backup_ui',
            # 'restore_ui=gdockutils.ui:restore_ui',
        ],
    }
)
