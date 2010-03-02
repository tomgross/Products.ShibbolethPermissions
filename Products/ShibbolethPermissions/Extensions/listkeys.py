## Script (Python) "listkeys"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=config
##title=Shibboleth Permissions
##
try:
    rval = config.keys()
except (AttributeError, TypeError):
    return []
rval.sort()
return rval
