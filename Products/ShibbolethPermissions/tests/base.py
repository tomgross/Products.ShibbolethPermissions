from Products.PloneTestCase import PloneTestCase as ptc
from Products.ShibbolethPermissions.tests.utils import addShibbolethPermissions


ptc.setupPloneSite()
ptc.installProduct('ShibbolethPermissions')


class ShibPermTestCase(ptc.PloneTestCase):
    """ A base class for ShibbolethPermissions tests """


class ShibPermFunctionalTestCase(ptc.FunctionalTestCase):
    """ A base class for ShibbolethPermissions functional tests """

    def afterSetUp(self):
        addShibbolethPermissions(self.portal)

# EOF
