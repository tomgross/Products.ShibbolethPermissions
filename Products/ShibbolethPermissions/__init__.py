#
from AccessControl.Permissions import view
from Products.PluggableAuthService import registerMultiPlugin
try:
    from ShibbolethPermissions.permissions import ShibbolethPermissionsHandler
except ImportError:
    from Products.ShibbolethPermissions.permissions import ShibbolethPermissionsHandler
try:
    from ShibbolethPermissions import zmi
except ImportError:
    from Products.ShibbolethPermissions import zmi
from Products.CMFCore.utils import getToolByName

try:
    registerMultiPlugin(ShibbolethPermissionsHandler.meta_type)
except RuntimeError:
    pass

shib_globals = globals()        # for Extensions/Install.py

def initialize(context):
    """Intializer called when used as a Zope 2 product."""
    context.registerClass(ShibbolethPermissionsHandler,
                          permission=view,
                          constructors=(zmi.manage_addShibbolethPermissionsForm,
                                        zmi.manage_addShibbolethPermissions),
                          visibility=None,
                          icon='shibbolethlogin.gif')
#    try:
#        portal_kss = getToolByName(context, 'portal_kss') # new in 3.0
#        from Products.CMFPlone.interfaces import IPloneSiteRoot
#        from Products.GenericSetup import EXTENSION, profile_registry
#        profile_registry.registerProfile('default',
#                                         'Shibboleth Permissions',
#                                         'Grant permissions to new users',
#                                         'profiles/default',
#                                         'ShibbolethPermissions',
#                                         EXTENSION,
#                                         for_=IPloneSiteRoot)
#    except AttributeError:
#        pass
