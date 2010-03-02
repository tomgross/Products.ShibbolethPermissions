## Script (Python) "folder_localrole_shib_upd"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=physicalPath, row_number=[], member_role=()
##title=Shibboleth Permissions
##
from Products.CMFCore.utils import getToolByName
#from Products.PluggableAuthService.PluggableAuthService import logger
#logger.info("folder_localrole_shib_add row_number = %s" % repr(row_number))
#logger.info("folder_localrole_shib_add member_role = %s" % repr(member_role))
acl_users = getToolByName(context, 'acl_users')
row_number.sort(reverse=True)
for ii in row_number:
    try:
        if ii:
            acl_users.ShibbolethPermissions.updLocalRoles(physicalPath, int(ii), member_role)
    except (TypeError, IndexError):
        pass
context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form')
