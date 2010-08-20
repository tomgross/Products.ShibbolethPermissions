# -*- coding: utf-8 -*-
"""
This module contains the Zope2 product ShibbolethPermissions: A Plone customization
"""
import os
from setuptools import setup, find_packages
def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.8a2 (svn/unreleased)'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('Products', 'ShibbolethPermissions', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

setup(name='Products.ShibbolethPermissions',
      version=version,
      description="Use shibboleth attributes as authenitcation information in Plone",
      long_description=long_description,
      classifiers=[
        'Framework :: Zope2',
        'Framework :: Plone',
        'Programming Language :: Python',
        ],
      keywords='plone authentication shibboleth pas',
      author='Tom Gross',
      author_email='itconsense@gmail.com',
      url='http://pypi.python.org/pypi/Products.ShibbolethPermissions/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'plone.app.workflow',
          'plone.memoize',
          'setuptools',
          'zope.component',
          ],
      entry_points=""" """,
      )
