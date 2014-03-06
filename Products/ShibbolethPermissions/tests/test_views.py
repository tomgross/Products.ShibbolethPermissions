import unittest

from Products.ShibbolethPermissions.tests.base import ShibPermTestCase
from Products.ShibbolethPermissions.tests.utils import addShibbolethPermissions

from Products.ShibbolethPermissions.browser.permissions import _getList
from Products.ShibbolethPermissions.browser.permissions import ShibbolethView

class ShibbolethViewTests(ShibPermTestCase):

    def afterSetUp(self):
        addShibbolethPermissions(self.portal)

    def test_getlist(self):
        self.assertEqual(_getList({}, 'foo'), [])
        self.assertEqual(_getList({'hello': 'world'}, 'hello'), ['world',])
        self.assertEqual(_getList({'bar': [1, 2]}, 'bar'), [1, 2])

    def test_roles(self):
        context = self.portal
        request = self.portal.REQUEST
        view = ShibbolethView(context, request)
        self.assertEqual(view.roles(), [])

    def test_shibattrs(self):
        context = self.portal
        request = self.portal.REQUEST
        view = ShibbolethView(context, request)
        self.assertEqual(view.shibattrs(), [])

    def test_shibperms(self):
        context = self.portal
        request = self.portal.REQUEST
        view = ShibbolethView(context, request)
        self.assertEqual(view.shibperms(), [])

    def test_listkeys(self):
        context = self.portal
        request = self.portal.REQUEST
        view = ShibbolethView(context, request)
        self.assertEqual(view.listkeys({}), [])

        self.assertEqual(view.listkeys(None), [])
        self.assertEqual(view.listkeys({'b': 1, 'c': 3, 'a': 2}),
                         ['a', 'b', 'c'])

    def test_cancel_view(self):
        context = self.portal
        request = self.portal.REQUEST
        request.form['form.button.Cancel'] = 1
        view = ShibbolethView(context, request)
        self.failIf(view()) # the view is none itself, but redirects
        resp = request.response
        self.assertEqual(resp.getStatus(), 302)
        self.assertEqual(resp.getHeader('location'), 'http://nohost/plone')

def test_suite():
    """ This is the unittest suite """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

# EOF
