from Products.PluggableAuthService.interfaces.authservice import IPluggableAuthService
from Products.ShibbolethPermissions.permissions import ShibbolethPermissionsHandler
from Products.ShibbolethPermissions.Extensions.Install import _firstIdOfClass

def addShibbolethPermissions(context):
    """Find the nearest acl_users and adds and activates an ShibbolethPermissions.

    Return a 1-tuple with the new ShibbolethPermissions as its only element."""

    acl_users = getattr(context, 'acl_users', None)
    if acl_users is None:
        raise LookupError("No acl_users can be acquired or otherwise found.")

    pas = IPluggableAuthService(acl_users, None)
    if pas is None:
        raise ValueError("The nearest acl_users object is not a PluggableAuthService.")

    pluginId = _firstIdOfClass(acl_users, ShibbolethPermissionsHandler)
    if not pluginId:
        pluginId = 'ShibbolethPermissions'
        setup = acl_users.manage_addProduct[pluginId]
        setup.manage_addShibbolethPermissions(pluginId, 'ShibbolethPermissions')

    return pas[pluginId]
