def importVarious(context):
    logger = context.getLogger('PluggableAuthService')
    if context.readDataFile('ShibbolethPermissions.policy_various.txt') is None:
        return
    site = context.getSite()
    diff = site.portal_actions.object.getObjectPosition('shibboleth') - \
        site.portal_actions.object.getObjectPosition('local_roles') -1
    if diff > 0:
        for ii in range(diff):
            try:
                site.portal_actions.object.manage_move_objects_up(context, ids=('shibboleth',))
            except Exception, e:
                logger.warning("cannot move shibboleth up: %s" % str(e))
