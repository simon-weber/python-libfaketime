#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import sys


# This hack is from http://stackoverflow.com/a/7071358/1231454;
# the version is kept in a seperate file and gets parsed - this
# way, setup.py doesn't have to import the package.

VERSIONFILE = 'libfaketime/_version.py'

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(version_re, version_line, re.M)
if match:
    version = match.group(1)
else:
    raise RuntimeError("Could not find version in '%s'" % VERSIONFILE)


if sys.platform == "linux" or sys.platform == "linux2":
    faketime_lib = '../vendor/libfaketime/src/libfaketime.so.1'
elif sys.platform == "darwin":
    faketime_lib = '../vendor/libfaketime/src/libfaketime.1.dylib'
else:
    raise RuntimeError("libfaketime does not support platform %s" % sys.platform)


class CustomInstall(install):
    def run(self):
        subprocess.check_call(['make', '-C', 'vendor/libfaketime'])
        install.run(self)

setup(
    name='libfaketime',
    version=version,
    author='Simon Weber',
    author_email='simon@simonmweber.com',
    url='http://pypi.python.org/pypi/libfaketime/',
    packages=find_packages(),
    scripts=[],
    license=open('LICENSE').read(),
    description='A fast alternative to freezegun that wraps libfaketime.',
    long_description=(open('README.rst').read()),
    package_data={'libfaketime': [faketime_lib]},
    install_requires=[
        'contextdecorator',
        'python-dateutil >= 1.3, != 2.0',         # 2.0 is python3-only
    ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data=True,
    zip_safe=False,
    cmdclass={'install': CustomInstall},
)
