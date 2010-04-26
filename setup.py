# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.plonefinder
"""
import os
from setuptools import setup, find_packages

version = '1.0.0a'

setup(name='collective.plonefinder',
      version=version,
      description="A finder to search/select portal objects for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='Zope Plone Medias Finder',
      author='Alter Way Solutions',
      author_email='support@ingeniweb.com',
      url='http://www.alterway.fr',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- entry_points -*- 
      """,
      )
