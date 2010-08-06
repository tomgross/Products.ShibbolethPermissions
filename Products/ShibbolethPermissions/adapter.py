from zope.interface import Interface, implements
from zope.component import adapts
from borg.localrole.interfaces import ILocalRoleProvider

from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

from Products.Archetypes.interfaces import IBaseObject

from Acquisition import aq_inner

class ShibLocalRoleAdapter(object):
    """ Looks at shibboleth headers to find local roles
    """

    implements(ILocalRoleProvider)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context

    def getRoles(self, principal_id):
        """ Returns the roles for the given principal in context
        """
        portal_state = self.context.restrictedTraverse('@@plone_portal_state')
        portal = portal_state.portal()
        acl_users = portal['acl_users']
        try:
            shibPerms = acl_users['ShibbolethPermissions']
            usermaker = acl_users['AutoUserMakerPASPlugin']
        except KeyError:
            return []
        uservals = usermaker.getshibattrs()
        if not uservals:
            return []

        localroles = shibPerms.getLocalRoles()
        regexs = localroles.get('/'.join(self.context.getPhysicalPath()), None)
        if regexs == None:
            return []

        for ii in regexs:
            found = True
            # Make sure the incoming user has all of the
            # needed attributes
            for name in ii.iterkeys():
                if name == '_roles':
                    continue
                if not uservals.has_key(name):
                    found = False
                if not found:
                    break
            if found:
                for name, pattern in ii.iteritems():
                    if name == '_roles' or uservals[name] is None:
                        continue
                    try:
                        regex = re.compile(pattern)
                        if not regex.search(uservals[name]):
                            found = False
                    except (ConflictError, KeyboardInterrupt):
                        raise
                    except Exception, e:
                        pass
                    if not found:
                        break
            if found:
                return ii['_roles']
        return []

    def getAllRoles(self):
        """ Returns all the local roles assigned in this context:
            (principal_id, [role1, role2])
        """
        return ()
