from Products.PloneTestCase import PloneTestCase as ptc

ptc.setupPloneSite()
ptc.installProduct('AutoUserMakerPASPlugin')
ptc.installProduct('ShibbolethPermissions')

class ShibPermTestCase(ptc.PloneTestCase):
    """ A base class for ShibbolethPermissions tests """

from Products.ShibbolethPermissions.tests.utils import addShibbolethPermissions
from Products.AutoUserMakerPASPlugin.tests.utils import \
    addAutoUserMakerPASPlugin

class ShibPermFunctionalTestCase(ptc.FunctionalTestCase):
    """ A base class for ShibbolethPermissions functional tests """


    def afterSetUp(self):
        addAutoUserMakerPASPlugin(self.portal)
        addShibbolethPermissions(self.portal)

