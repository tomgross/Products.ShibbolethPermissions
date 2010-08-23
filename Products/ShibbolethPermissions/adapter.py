import re
from zope.interface import Interface, implements
from zope.component import adapts
from borg.localrole.interfaces import ILocalRoleProvider

from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

from Products.Archetypes.interfaces import IBaseObject

from Acquisition import aq_inner, aq_parent, aq_chain

class ShibLocalRoleAdapter(object):
    """ Looks at shibboleth headers to find local roles
    """

    implements(ILocalRoleProvider)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context


    def _findroles(self, context, rolemap, uservals):
        regexs = rolemap.get('/'.join(context.getPhysicalPath()), None)
        if regexs == None:
            return []

        for ii in regexs:
            # Make sure the incoming user has all of the
            # needed attributes
            for name in ii.iterkeys():
                if name == '_roles':
                    continue
                if not name in uservals:
                    break
            else:
                for name, pattern in ii.iteritems():
                    if name == '_roles' or uservals[name] is None:
                        continue
                    try:
                        regex = re.compile(pattern)
                        if not regex.search(uservals[name]):
                            break
                    except (ConflictError, KeyboardInterrupt):
                        raise
                    except Exception, e:
                        break
                else:
                    return list(ii['_roles'])
        return []


    def getRoles(self, principal_id):
        """ Returns the roles for the given principal in context
        """
        portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
        portal = portal_state.portal()
        acl_users = portal['acl_users']
        try:
            shibPerms = acl_users['ShibbolethPermissions']
            borg = acl_users['borg_localroles']
        except KeyError:
            return []

        uservals = shibPerms.getShibValues()
        if not uservals:
            return []

        localroles = shibPerms.getLocalRoles()
        roles = []
        for obj in borg._parent_chain(self.context):
            roles.extend(self._findroles(obj, localroles, uservals))
            if obj == portal:
                break
        return roles

    def getAllRoles(self):
        """ Returns all the local roles assigned in this context:
            (principal_id, [role1, role2])
        """
        return ()
