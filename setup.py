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

version = read('collective', 'plonefinder', 'version.txt')

setup(name='collective.plonefinder',
      version=version,
      description="A finder to search/select portal objects for Plone",
      long_description=(read("README.txt")
                        + "\n\n"
                        +read("docs", "HISTORY.txt")),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Framework :: Plone',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'License :: OSI Approved :: GNU General Public License (GPL)',
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
