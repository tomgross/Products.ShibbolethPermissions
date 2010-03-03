from Products.PloneTestCase import PloneTestCase as ptc

ptc.setupPloneSite()
ptc.installProduct('AutoUserMakerPASPlugin')
ptc.installProduct('ShibbolethPermissions')

class ShibPermTestCase(ptc.PloneTestCase):
    """ A base class for ShibbolethPermissions tests """

class ShibPermFunctionalTestCase(ptc.FunctionalTestCase):
    """ A base class for ShibbolethPermissions functional tests """
