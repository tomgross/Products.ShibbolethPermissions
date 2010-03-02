## Script (Python) "folder_localrole_shib_add"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=physicalPath, attribs=(), values=(), member_role=()
##title=Shibboleth Permissions
##
from Products.CMFCore.utils import getToolByName
shibattr = {}
for ii in range(len(attribs)):
    try:
        if values[ii]:
            shibattr[attribs[ii]] = values[ii]
    except IndexError:
        break
if shibattr and member_role:
    acl_users = getToolByName(context, 'acl_users')
    acl_users.ShibbolethPermissions.addLocalRoles(physicalPath, shibattr, member_role)
context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/folder_localrole_form')
