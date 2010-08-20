import unittest

from Products.ShibbolethPermissions.tests.base import ShibPermTestCase
from Products.ShibbolethPermissions.tests.utils import addShibbolethPermissions

from Products.ShibbolethPermissions.adapter import ShibLocalRoleAdapter

class ShibbolethAdapterTests(ShibPermTestCase):

    def afterSetUp(self):
        addShibbolethPermissions(self.portal)
        self.folder.invokeFactory('Folder', 'layer1a')
        self.folder.layer1a.invokeFactory('Folder', 'layer2a')
        self.folder.invokeFactory('Folder', 'layer1b')
        acl_users = self.portal.acl_users
        self.plugin = acl_users.ShibbolethPermissions
        self.plugin.manage_changeProperties(
            {'http_sharing_tokens': ['HTTP_DUMMY_ATTR']})
        path = '/'.join(self.folder.layer1a.getPhysicalPath())
        self.plugin.addLocalRoles(path, {'HTTP_DUMMY_ATTR': 'eggs'},
                                  ['Editor',])

    def test_getroles_empty(self):
        adapter = ShibLocalRoleAdapter(self.folder)
        self.assertEqual(adapter.getRoles('foo'), [])

    def test_getroles(self):
        adapter = ShibLocalRoleAdapter(self.folder.layer1a)
        self.assertEqual(adapter.getRoles('foo'), [])

        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = 'eggs'
        self.assertEqual(adapter.getRoles('foo'), ['Editor'])

        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = 'bogus'
        self.assertEqual(adapter.getRoles('foo'), [])

        self.app.REQUEST.environ['HTTP_ANOTHER_ATTR']  = 'eggs'
        self.assertEqual(adapter.getRoles('foo'), [])


    def test_getroles_inherited(self):
        path = '/'.join(self.folder.layer1a.layer2a.getPhysicalPath())
        self.plugin.addLocalRoles(path, {'HTTP_DUMMY_ATTR': 'eggs'},
                                  ['Contributor'])

        adapter = ShibLocalRoleAdapter(self.folder.layer1a.layer2a)
        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = 'eggs'
        self.assertEqual(adapter.getRoles('foo'), ['Contributor', 'Editor'])



    def test_getallroles(self):
        adapter = ShibLocalRoleAdapter(self.folder)
        self.assertEqual(adapter.getAllRoles(), ())

def test_suite():
    """ This is the unittest suite """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

# EOF
