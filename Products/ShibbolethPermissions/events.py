import logging

log = logging.getLogger('ShibbolethPermissions')

def refreshlocalroles(event):
    user = event.principal
    if hasattr(user, '_getPAS'):
        pas = user._getPAS()
    else:
        log.warn(("PAS not found! Cannot refresh local roles."))
        return
    if 'ShibbolethPermissions' not in pas.keys():
        log.warn(("ShibbolethPermissions plugin not found! "
                  "Cannot refresh local roles."))
        return
    shibtool = pas['ShibbolethPermissions']
    shibtool.refreshlocalroles(user)

# EOF
