## Script (Python) "formatattr"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=entry
##title=Format Attributes
##
from Products.CMFCore.utils import getToolByName
acl_users = getToolByName(context, 'acl_users')
return acl_users.ShibbolethPermissions.formatAttrList(entry)
