"""Run bin/zopectl test -s Products.ShibbolethPermissions.

add " -m '.*txtfiles.*'" to run just this test set."""

__revision__ = '0.1'

import glob
import os
import unittest
from zope.testing import doctest
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Globals import package_home
try:
    from ShibbolethPermissions import shib_globals
    package = 'ShibbolethPermissions'
except ImportError:
    from Products.ShibbolethPermissions import shib_globals
    package = 'Products.ShibbolethPermissions'

ptc.setupPloneSite()
ptc.installProduct('AutoUserMakerPASPlugin')
ptc.installProduct('ShibbolethPermissions')

def listDoctests():
    home = package_home(shib_globals)
    return [ii for ii in glob.glob(os.path.sep.join([home + '/tests', '*.txt']))]

def test_suite():
    files = listDoctests()
    tests = [ztc.FunctionalDocFileSuite('tests/' + os.path.basename(filename),
                                        test_class=ptc.PloneTestCase,
                                        package=package,
                                        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE)
             for filename in files]
    return unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')