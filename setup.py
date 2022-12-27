#  ------------------------------------------
#   Copyright (c) Rygor. 2022.
#  ------------------------------------------

"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages
from omni import __version__

setup(
    name='omnifocus-from-command-line',
    version=__version__,
    license='MIT',
    description='OmniFocus Mail Drop from command line',

    author='Rygor',
    author_email='pisemco@gmail.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['click', 'click_log', 'rich_click'],

    entry_points={
        'console_scripts': [
            'omni = omni.cli:omni_cli',
        ]
    },
)
