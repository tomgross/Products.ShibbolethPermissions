"""Classes to manage local permissions from Shibboleth attributes.
"""
__revision__ = '0.1'

import re
import logging

from AccessControl import ClassSecurityInfo
from ZODB.POSException import ConflictError
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _getAuthenticatedUser
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.PluggableAuthService import logger
from persistent.dict import PersistentDict
from persistent.list import PersistentList

try:
    from Products.AutoUserMakerPASPlugin.auth import httpSharingTokensKey
    from Products.AutoUserMakerPASPlugin.auth import httpSharingLabelsKey
    httpSharingTokensKey, httpSharingLabelsKey  # pyflakes
    IS_AUMPAS_INSTALLED = True
except ImportError:
    httpSharingTokensKey = 'http_sharing_tokens'
    httpSharingLabelsKey = 'http_sharing_labels'
    IS_AUMPAS_INSTALLED = False

log = logging.getLogger('shibboleth')

def _searchParams(pathList, paramKeys, **params):
    """Return a list of dictionaries of matched params.

    pathList is what is configure for the path we're searching.
    paramKeys is the sorted list of **params' keys.
    """
    rval = []
    for ii in pathList:
        pathKeys = ii.keys()
        pathKeys.sort()
        if pathKeys != paramKeys:
            continue       # both the subcriteria and source dictionary
                            # must have the same set of keys
        regexes = dict([(key, re.compile(ii[key])) for key in paramKeys])
        for jj in paramKeys:
            found = regexes[jj].search(params[jj]) and True or False
            if not found:
                break # This doesn't match, so no point in testing more
        else: # Got here as true, so it matched all, save it
            rval.append(ii)
    return rval


class ShibbolethPermissions(BasePlugin):
    """Extend folder_localrole_form to grant permissions to Shibboleth users.

    Most testing is done in tests/ShibbolethPermissions.txt."""
    security = ClassSecurityInfo()

    def __init__(self, pluginId, title=None):
        self.setId(pluginId)
        self.title = title
        self.localRoles = PersistentDict()
        self.retest = re.compile(' ')
        config = ((httpSharingTokensKey, 'lines', 'w', []),
                  (httpSharingLabelsKey, 'lines', 'w', []))
        # Create any missing properties
        ids = {}
        for prop in config:
            # keep track of property names for quick lookup
            ids[prop[0]] = True
            if prop[0] not in self.propertyIds():
                self.manage_addProperty(id=prop[0],
                                        type=prop[1],
                                        value=prop[3])
                self._properties[-1]['mode'] = prop[2]
        # Delete any existing properties that aren't in config
        ids.update({'prefix':'', 'title':''})
        for prop in self._properties:
            if prop['id'] not in ids:
                self.manage_delProperties(prop['id'])

    security.declarePublic('getSharingConfig')
    def getSharingConfig(self):
        """Return the items end users can use to share with.

        Verify it returns an empty configuration.
        >>> from Products.ShibbolethPermissions.permissions import ShibbolethPermissions
        >>> handler = ShibbolethPermissions()
        >>> handler.getSharingConfig()
        {'http_sharing_tokens': (), 'http_sharing_labels': ()}
        """
        if IS_AUMPAS_INSTALLED:
            autoUserMaker = getToolByName(self, 'AutoUserMakerPASPlugin', None)
            if autoUserMaker is not None:
                return autoUserMaker.getSharingConfig()
        return {httpSharingTokensKey: self.getProperty(httpSharingTokensKey),
                 httpSharingLabelsKey: self.getProperty(httpSharingLabelsKey)}

    security.declarePrivate('getShibValues')
    def getShibValues(self):
        config = self.getSharingConfig()
        request = getattr(self, 'REQUEST')
        req_environ = getattr(request, 'environ', {})
        return dict([(ii, req_environ.get(ii))
                     for ii in config[httpSharingTokensKey]
                     if ii in req_environ])

    security.declarePublic('getLocalRoles')
    def getLocalRoles(self, path=None, **params):
        """Return the self.localRoles as a dictionary or list.

        Return a dictionay if neither path nor params is set (whole dictionary
        of lists of dictionaries). Return a dictionary if params is set, but
        path is not (subset of the whole dictionary of lists of dictionaries).
        Return a list of dictionaries when path is set, which may be an empty
        list if the path is not found or params is given in addition to path
        and none of the params match.

        This simple test returns everything, which at this point is nothing.
        """
        roles = {}
        param_keys = params.keys().sort()
        for ii in self.localRoles.iterkeys():
            roles[ii] = list(self.localRoles[ii])
        if not path and not params:
            return roles        # no select given, so return everything
        if path:
            if not path in roles:
                return []   # path not found, so return nothing
            if not params:  # path found, but no subcriteria so return whole list
                return roles[path]
            return _searchParams(roles[path], param_keys, **params)
        # no path, but params, so return a path keyed dict of lists of dicts
        rval = {}
        for ii in roles.iterkeys():  # each key is a Plone path
            found = _searchParams(roles[ii], param_keys, **params)
            if found:           # Don't save empty lists
                rval[ii] = found
        return rval

    security.declarePublic('addLocalRoles')
    def addLocalRoles(self, path, params, roles):
        """Add a pattern for path of params."""
        params['_roles'] = roles
        if path in self.localRoles:
            self.localRoles[path].append(params)
        else:
            self.localRoles[path] = PersistentList([params,])

    security.declarePublic('delLocalRoles')
    def delLocalRoles(self, path=None, row=None):
        """ Delete the specified roles.
        """
        if path is None and row is None:
            self.localRoles.clear()
        elif path in self.localRoles:
            if row is not None:
                del self.localRoles[path][row]
            else:
                del self.localRoles[path]

    security.declarePublic('updLocalRoles')
    def updLocalRoles(self, path=None, row=None, roles=None):
        """ Update the specified roles.
        """
        if roles is None:
            roles = []
        if path and path in self.localRoles and row is not None:
            try:
                self.localRoles[path][row]['_roles'] = roles
            except (IndexError, TypeError):
                logger.warning("updLocalRoles error updating row %s from %s"
                               % (str(row), str(path)), exc_info=True)

    def _findroles(self, context):
        uservals = self.getShibValues()
        regexs = self.getLocalRoles().get('/'.join(context.getPhysicalPath()), None)
        if regexs is None:
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
                    except Exception:
                        break
                else:
                    return list(ii['_roles'])
        return []

    def refreshlocalroles(self, user=None):
        if user is None:
            userid = _getAuthenticatedUser(None).getId()
        else:
            userid = user.getId()
        if not userid:
            return
        for path in self.localRoles.iterkeys():
            obj = self.unrestrictedTraverse(path, None)
            if obj is not None:
                roles = self._findroles(obj)
                reindex = False
                current_localroles = obj.get_local_roles_for_userid(userid)
                if not roles and current_localroles:
                    obj.manage_delLocalRoles((userid,))
                    reindex = True
                elif tuple(roles) != current_localroles:
                    obj.manage_setLocalRoles(userid, roles)
                    reindex = True
                if reindex:
                    obj.reindexObjectSecurity()


class ShibbolethPermissionsHandler(ShibbolethPermissions):
    """Provide a basic ZMI interface for managing mappings.

    Most of the testing happens in tests/ShibbolethPermissions.txt."""

    meta_type = 'Shibboleth Permissions'
    security = ClassSecurityInfo()

    # A method to return the configuration page:
    security.declareProtected(ManageUsers, 'manage_config')
    manage_config = PageTemplateFile('config', globals())

    # Add a tab that calls that method:
    manage_options = ({'label': 'Manage', 'action': 'manage_config'},) \
                   + BasePlugin.manage_options

    security.declareProtected(ManageUsers, 'manage_changeMapping')
    def manage_changeMapping(self, REQUEST=None):
        """Update my configuration based on form data.

        Verify it returns nothing. More testing is done in the integration file.
        >>> from Products.ShibbolethPermissions.auth import \
                ShibbolethPermissionsHandler
        >>> handler = ShibbolethPermissionsHandler('someId')
        >>> handler.manage_changeConfig()

        """
        if not REQUEST:
            return None
        reqget = REQUEST.form.get
        # Save the form values
        self.manage_changeProperties({
            httpSharingTokensKey: reqget(httpSharingTokensKey, ''),
            httpSharingLabelsKey: reqget(httpSharingLabelsKey, '')})
        return REQUEST.RESPONSE.redirect('%s/manage_config' %
                                         self.absolute_url())

    security.declarePublic('listKeys')
    def listKeys(self, config):
        """Return sorted keys of config.
        """
        if hasattr(config, 'keys'):
            return sorted(config.keys())
        else:
            return []

    security.declarePublic('getShibAttrs')
    def getShibAttrs(self):
        """Return a list of (label, attribute) tupples."""
        config = self.getSharingConfig()
        rval = []
        for ii, token in enumerate(config[httpSharingTokensKey]):
            try:
                rval.append((config[httpSharingLabelsKey][ii],
                             token))
            except IndexError:
                rval.append((token, token))
        return rval

    security.declareProtected(ManageUsers, 'manage_changeConfig')
    def manage_changeConfig(self, REQUEST=None):
        """Delete given paths."""
        if not REQUEST:
            return None
        for ii in REQUEST.form.get('plonepath', []):
            self.delLocalRoles(ii)
        return REQUEST.RESPONSE.redirect('%s/manage_config' %
                                         self.absolute_url())

    security.declarePublic('isAutoUserMakerPASinstalled')
    def isAutoUserMakerPASinstalled(self):
        return IS_AUMPAS_INSTALLED and \
               'AutoUserMakerPASPlugin' in self._getPAS().objectIds()

InitializeClass(ShibbolethPermissionsHandler)
