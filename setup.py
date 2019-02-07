##############################################################################
#
# Copyright (c) 2008 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = '0.8.3'

import os

from setuptools import setup, find_packages

try:
    here = os.path.abspath(os.path.dirname(__file__))
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

INSTALL_REQUIRES = [
    'setuptools',
    'zope.component',
    'ZODB3',
    'zope.index >= 3.5.0',
]

TESTING_EXTRAS = ['nose', 'coverage']
DOCS_EXTRAS = ['Sphinx']

setup(name='repoze.catalog',
      version=__version__,
      description='Searching and indexing based on zope.index',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        ],
      keywords='indexing catalog search',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      tests_require = INSTALL_REQUIRES,
      install_requires = INSTALL_REQUIRES,
      extras_require = {
            'benchmark': ['PyChart'],
            'testing': TESTING_EXTRAS,
            'docs': DOCS_EXTRAS,
        },
      test_suite="repoze.catalog",
      ## entry_points = """\
      ## [console_scripts]
      ## catalog_benchmark = repoze.catalog.benchmark.benchmark:run
      ## sortbench = repoze.catalog.benchmark.sortbench:main
      ## """,
)
