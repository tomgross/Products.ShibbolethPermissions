#
from AccessControl.Permissions import view
from Products.PluggableAuthService import registerMultiPlugin

from Products.ShibbolethPermissions.permissions import ShibbolethPermissionsHandler
from Products.ShibbolethPermissions import zmi

registerMultiPlugin(ShibbolethPermissionsHandler.meta_type)
shib_globals = globals()        # for Extensions/Install.py

def initialize(context):
    """Intializer called when used as a Zope 2 product."""
    context.registerClass(ShibbolethPermissionsHandler,
                          permission=view,
                          constructors=(zmi.manage_addShibbolethPermissionsForm,
                                        zmi.manage_addShibbolethPermissions),
                          visibility=None,
                          icon='shibbolethlogin.gif')
