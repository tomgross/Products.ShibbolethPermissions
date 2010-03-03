# This lets you install ShibbolethPermissions through Plone, 
# if you're into that.
# If you aren't using Plone, it doesn't hurt anything.

from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.PluggableAuthService import logger

from Products.ShibbolethPermissions.permissions import \
        ShibbolethPermissionsHandler
from Products.AutoUserMakerPASPlugin.Extensions.Install import _firstIdOfClass

def install(portal, reinstall=False):
    acl_users = getToolByName(portal, 'acl_users')

    # Put a ShibbolethPermisssion in the acl_users folder, if there isn't one:
    pluginId = _firstIdOfClass(acl_users, ShibbolethPermissionsHandler)
    if not pluginId:
        pluginId = 'ShibbolethPermissions'
        constructors = acl_users.manage_addProduct[pluginId]
        constructors.manage_addShibbolethPermissions(
            pluginId, title='ShibbolethPermissions Plugin')

    portal_setup = getToolByName(portal, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile(
        "profile-Products.ShibbolethPermissions:default", purge_old=False)

    # Now restore the configuration
    if reinstall:
        import pickle
        plugin = getattr(acl_users.plugins, pluginId)
        # Get the configuration out of the property, and delete the property.
        prop = "\n".join(acl_users.getProperty('sp_config'))
        config = pickle.loads(prop)
        roles = acl_users.portal_role_manager.listRoleIds()
        logger.info("roles = %s" % str(roles))
        for path in config.iterkeys():
            for entry in config[path]:
                thisRole = [role for role in entry['_roles'] if role in roles]
                thisParam = entry
                del thisParam['_roles']
                plugin.addLocalRoles(path, thisParam, thisRole)
    acl_users.manage_delProperties(['sp_config'])

def uninstall(portal, reinstall=False):
    acl_users = getToolByName(portal, 'acl_users')
    pluginId = _firstIdOfClass(acl_users, ShibbolethPermissionsHandler)
    if pluginId:
        if reinstall:
            import pickle
            plugin = getattr(acl_users.plugins, pluginId)
            config = plugin.getLocalRoles()
            conf = pickle.dumps(config)
            acl_users.manage_addProperty(id='sp_config',
                                         type='lines',
                                         value=conf)
        acl_users.manage_delObjects(ids=[pluginId])  # implicitly deactivates
