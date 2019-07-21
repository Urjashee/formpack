#!/usr/bin/env python
# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import re
import sys
from setuptools import setup, find_packages


requirements = [
    'begins',
    'cyordereddict',
    'jsonschema',
    'lxml',
    'path.py<12', # Pinned for Python 2 compatibility
    'pyquery',
    'pyxform',
    'statistics',
    'XlsxWriter',
    'backports.csv', # Remove after dropping Python 2 support (and rewrite `imports`)
    'geojson-rewind==0.1.1+py2.jnm', # Stop using fork after dropping Python 2 support
]
dep_links = [
    # "Be careful with the version" part of `#egg=project-version`, according to
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#dependencies-that-aren-t-in-pypi.
    # "It should match the one inside the project files," i.e. the `version`
    # argument to `setup()` in `setup.py`. It should also adhere to PEP 440.
    'https://github.com/jnm/geojson-rewind/tarball/master#egg=geojson-rewind-0.1.1+py2.jnm'
]

setup(name='formpack',
      version='1.4',
      description='Manipulation tools for kobocat forms',
      author='Alex Dorey',
      author_email='alex.dorey@kobotoolbox.org',
      url='https://github.com/kobotoolbox/formpack/',
      packages=[str(pkg) for pkg in find_packages('src')],
      package_dir={'': b'src'},
      install_requires=requirements,
      dependency_links=dep_links,
      include_package_data=True,
      zip_safe=False,
      )
