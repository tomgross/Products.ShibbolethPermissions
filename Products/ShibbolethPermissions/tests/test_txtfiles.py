"""Run bin/zopectl test -s Products.ShibbolethPermissions.

add " -m '.*txtfiles.*'" to run just this test set."""

__revision__ = '0.1'

import glob
import os
import unittest
import doctest
from Testing import ZopeTestCase as ztc
from Products.ShibbolethPermissions import shib_globals

from Products.ShibbolethPermissions.tests.base import ShibPermFunctionalTestCase

def listDoctests():
    return glob.glob(os.path.join(os.path.dirname(__file__), '*.txt'))

def test_suite():
    tests = [ztc.FunctionalDocFileSuite(
                'tests/' + os.path.basename(filename),
                test_class=ShibPermFunctionalTestCase,
                package='Products.ShibbolethPermissions',
                optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
             for filename in listDoctests()]
    return unittest.TestSuite(tests)
