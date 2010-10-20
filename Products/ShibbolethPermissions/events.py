def refreshlocalroles(event):
    user = event.principal
    pas = user._getPAS()

    shibtool = pas['ShibbolethPermissions']
    shibtool.refreshlocalroles(user)

# EOF
