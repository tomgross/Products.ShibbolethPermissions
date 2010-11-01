import logging

log = logging.getLogger('ShibbolethPermissions')

def refreshlocalroles(event):
    user = event.principal
    pas = user._getPAS()

    if 'ShibbolethPermissions' not in pas.keys():
        log.warn(("ShibbolethPermissions plugin not found! "
                  "Cannot refresh local roles."))
        return
    shibtool = pas['ShibbolethPermissions']
    shibtool.refreshlocalroles(user)

# EOF
