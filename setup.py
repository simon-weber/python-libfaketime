#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys


# This hack is from http://stackoverflow.com/a/7071358/1231454;
# the version is kept in a seperate file and gets parsed - this
# way, setup.py doesn't have to import the package.

VERSIONFILE = 'libfaketime_tz_wrapper/_version.py'

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(version_re, version_line, re.M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)

setup(
    name='libfaketime-tz-wrapper',
    version=version,
    author='Joppe Geluykens and Roeland Matthijssens',
    author_email='joppe@youngwolves.co',
    url='https://github.com/jppgks/python-libfaketime',
    download_url='https://github.com/jppgks/python-libfaketime/tarball/0.1.3',
    packages=find_packages(exclude=['test']),
    scripts=[],
    license='GPLv2',
    description='A fast alternative to freezegun that wraps libfaketime.',
    long_description=(open('README.rst').read()),
    install_requires=[
        'libfaketime',
        'python-dateutil >= 1.3, != 2.0',         # 2.0 is python3-only
    ],
    extras_require={
        ':python_version=="2.7"': ['contextdecorator'],
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    zip_safe=False,
)
