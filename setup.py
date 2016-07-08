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

version = '1.2.0'

setup(name='collective.plonefinder',
      version=version,
      description="A finder to search/select portal objects for Plone",
      long_description=(read("README.rst")
                        + "\n\n"
                        +read("docs", "HISTORY.txt")),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Framework :: Zope2",
        "Framework :: Plone",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
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
          ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
