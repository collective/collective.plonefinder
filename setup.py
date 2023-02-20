# -*- coding: utf-8 -*-
# $Id$
"""collective.plonefinder package
"""
import os
from setuptools import setup, find_packages

def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = '2.0.0a1'

tests_require = [
    'plone.app.testing',
    ]

setup(name='collective.plonefinder',
      version=version,
      description="A finder to search/select portal objects for Plone",
      long_description=(read("README.rst")
                        + "\n\n"
                        +read("docs", "HISTORY.txt")),
      # Get more strings from https://pypi.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Framework :: Zope2",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='Zope Plone Medias Finder',
      author='Jean-mat Grimaldi / Alter Way Solutions',
      author_email='support@ingeniweb.com',
      url='http://www.alterway.fr',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.quickupload',
          'plone.api',
          ],
      extras_require={
          'test': tests_require,
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
