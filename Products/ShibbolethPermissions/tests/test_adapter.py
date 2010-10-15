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
        self.app.REQUEST.environ = {}

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

    def test_getroles_otherattr(self):
        self.plugin.manage_changeProperties(
            {'http_sharing_tokens': ['HTTP_DUMMY_ATTR', 'HTTP_ANOTHER_ATTR']})
        path = '/'.join(self.folder.layer1a.getPhysicalPath())
        self.plugin.delLocalRoles(path, 0)
        self.plugin.addLocalRoles(path, {'HTTP_DUMMY_ATTR': 'eggs',
                                         'HTTP_ANOTHER_ATTR': 'spam'},
                                  ['Custom',])
        adapter = ShibLocalRoleAdapter(self.folder.layer1a)
        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = 'eggs'
        self.assertEqual(adapter.getRoles('foo'), [])

    def test_getroles_inherited(self):
        path = '/'.join(self.folder.layer1a.layer2a.getPhysicalPath())
        self.plugin.addLocalRoles(path, {'HTTP_DUMMY_ATTR': 'eggs'},
                                  ['Contributor'])

        adapter = ShibLocalRoleAdapter(self.folder.layer1a.layer2a)
        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = 'eggs'
        self.assertEqual(adapter.getRoles('foo'), ['Contributor', 'Editor'])

        self.folder.layer1a.layer2a.__ac_local_roles_block__ = True
        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = 'eggs'
        adapter = ShibLocalRoleAdapter(self.folder.layer1a.layer2a)
        self.assertEqual(adapter.getRoles('foo'), ['Contributor'])

        delattr(self.folder.layer1a.layer2a, '__ac_local_roles_block__')

    def test_getallroles(self):
        adapter = ShibLocalRoleAdapter(self.folder)
        self.assertEqual(adapter.getAllRoles(), ())

    def test_brokenregex(self):
        path = '/'.join(self.folder.layer1a.getPhysicalPath())
        self.plugin.delLocalRoles(path, 0)
        self.plugin.addLocalRoles(path, {'HTTP_DUMMY_ATTR': '('}, ['Custom',])
        adapter = ShibLocalRoleAdapter(self.folder.layer1a)
        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = '('
        self.assertEqual(adapter.getRoles('foo'), [])

    def test_catalogquery(self):
        self.portal.acl_users._doAddUser('jsmith', 'secret', [], [])
        self.folder.invokeFactory('Folder', id='testfolder')
        tf = self.folder.testfolder
        tf.invokeFactory('Document', id='testdocument')
        self.login('jsmith')
        tfpath = tf.absolute_url(1)
        cat = self.portal.portal_catalog
        self.assertFalse(cat.searchResults(path=tfpath))
        self.plugin.addLocalRoles(
            tfpath, {'HTTP_DUMMY_ATTR': 'localedit'}, ['Reader',])
        self.app.REQUEST.environ['HTTP_DUMMY_ATTR']  = 'localedit'
        #self.folder.manage_setLocalRoles('jsmith', ['Reader',])
        #self.folder.reindexObjectSecurity()
        res = cat.searchResults(path=tfpath)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].getId, 'testfolder')


def test_suite():
    """ This is the unittest suite """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

# EOF
