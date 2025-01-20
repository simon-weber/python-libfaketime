#!/usr/bin/env python

import os
import re
import subprocess
import sys

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install

# This hack is from http://stackoverflow.com/a/7071358/1231454;
# the version is kept in a seperate file and gets parsed - this
# way, setup.py doesn't have to import the package.

VERSIONFILE = "libfaketime/_version.py"

version_line = open(VERSIONFILE).read()
version_re = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(version_re, version_line, re.M)
if match:
    version = match.group(1)
else:
    raise RuntimeError(f"Could not find version in '{VERSIONFILE}'")


_vendor_path = "libfaketime/vendor/libfaketime"
if sys.platform == "linux" or sys.platform == "linux2":
    libname = "libfaketime.so.1"
elif sys.platform == "darwin":
    libname = "libfaketime.1.dylib"

else:
    raise RuntimeError("libfaketime does not support platform {sys.platform}")

faketime_lib = os.path.join(_vendor_path, "src", libname)


class CustomInstall(install):
    def run(self):
        self.my_outputs = []
        if sys.platform in ("linux", "linux2"):
            subprocess.check_call(
                [
                    "env",
                    "FAKETIME_COMPILE_CFLAGS=-UFAKE_STAT -UFAKE_UTIME -UFAKE_SLEEP",
                    "make",
                    "-C",
                    _vendor_path,
                ]
            )
        elif sys.platform == "darwin":
            subprocess.check_call(["make", "-C", _vendor_path])

        dest = os.path.join(self.install_purelib, os.path.dirname(faketime_lib))
        try:
            os.makedirs(dest)
        except OSError as e:
            if e.errno != 17:
                raise
        print(faketime_lib, "->", dest)
        self.copy_file(faketime_lib, dest)
        self.my_outputs.append(os.path.join(dest, libname))

        install.run(self)

    def get_outputs(self):
        outputs = install.get_outputs(self)
        outputs.extend(self.my_outputs)
        return outputs


setup(
    name="libfaketime",
    version=version,
    author="Simon Weber",
    author_email="simon@simonmweber.com",
    url="http://pypi.python.org/pypi/libfaketime/",
    packages=find_packages(exclude=["test"]),
    scripts=[],
    license="GPLv2",
    description="A fast alternative to freezegun that wraps libfaketime.",
    long_description=(open("README.md").read() + "\n\n" + open("CHANGELOG.md").read()),
    long_description_content_type="text/markdown",
    install_requires=[
        "python-dateutil >= 1.3",
        "pytz",  # for pytz.timezone and pytz.utc
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    zip_safe=False,
    cmdclass={"install": CustomInstall},
    entry_points={
        "console_scripts": [
            "python-libfaketime = libfaketime:main",
        ]
    },
)
