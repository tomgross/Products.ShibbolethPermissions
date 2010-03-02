## Script (Python) "shibperms"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=here
##title=Shibboleth Permissions
##
from Products.CMFCore.utils import getToolByName
acl_users = getToolByName(context, 'acl_users')
return acl_users.ShibbolethPermissions.getLocalRoles('/'.join(here.getPhysicalPath()))
