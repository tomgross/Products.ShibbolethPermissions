"""Run bin/zopectl test -s Products.ShibbolethPermissions.

add " -m '.*docstring.*'" to run just this test set.
"""

__revision__ = '0.1'

import unittest
from Products.ShibbolethPermissions.tests.base import ShibPermTestCase
from Products.ShibbolethPermissions.permissions import ShibbolethPermissionsHandler

class ShibPermissionsHandlerTestCase(ShibPermTestCase):

    def test_searchparams(self):
        from Products.ShibbolethPermissions import permissions
        path = [{'a':'1'}, {'a':'1', 'b':'2'}, {'a':'1', 'b':'3'},
                {'a':'1', 'b':'2', 'c':'3'}, {'a':'1', 'c':'3'}]
        keys = ['a', 'b']
        params = {'a':'1', 'b':'2'}
        self.assertEqual(
            permissions._searchParams(path, keys, **params),
            [{'a': '1', 'b': '2'}])

    def test_listkeys(self):
        sph = ShibbolethPermissionsHandler('test')
        self.assertEqual(sph.listKeys({'b': 2, 'a': 1, 'c': 3}), ['a', 'b', 'c'])

    def test_getlocalroles(self):
        sph = ShibbolethPermissionsHandler('test')
        self.assertEqual(sph.getLocalRoles(), {})

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)