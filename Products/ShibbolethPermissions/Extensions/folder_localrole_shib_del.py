## Script (Python) "folder_localrole_shib_del"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=physicalPath, row_number=[], member_role=()
##title=Shibboleth Permissions
##
from Products.CMFCore.utils import getToolByName
acl_users = getToolByName(context, 'acl_users')
row_number.sort(reverse=True)
for ii in row_number:
    try:
        if ii:
            acl_users.ShibbolethPermissions.delLocalRoles(physicalPath, int(ii))
    except (TypeError, IndexError):
        pass
context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form')
