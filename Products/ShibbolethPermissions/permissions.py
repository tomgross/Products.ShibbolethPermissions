#!/usr/bin/env python
"""Classes to manage local permissions from Shibboleth attributes."""
___revision__ = '0.1'

import re

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.PluggableAuthService import logger
from persistent.dict import PersistentDict

def _searchParams(pathList, paramKeys, **params):
    """Return a list of dictionaries of matched params.

    pathList is what is configure for the path we're searching.
    paramKeys is the sorted list of **params' keys.
    **params is what we're given from Shibboleth.
    >>> from Products.ShibbolethPermissions import permissions
    >>> path = [{'a':'1'}, {'a':'1', 'b':'2'}, {'a':'1', 'b':'3'},
    ...         {'a':'1', 'b':'2', 'c':'3'}, {'a':'1', 'c':'3'}]
    >>> keys = ['a', 'b']
    >>> params = {'a':'1', 'b':'2'}
    >>> permissions._searchParams(path, keys, **params)
    [{'a': '1', 'b': '2'}]
    """
    rval = []
    for ii in pathList:
        pathKeys = ii.keys()
        pathKeys.sort()
        if pathKeys != paramKeys:
            continue        # both the subcriteria and source dictionary
                            # must have the same set of keys
        regexes = {}
        for jj in paramKeys:
            regexes[jj] = re.compile(ii[jj])
        for jj in paramKeys:
            found = regexes[jj].search(params[jj]) and True or False
            if not found:
                break       # This doesn't match, so no point in testing more
        if found:           # Got here as true, so it matched all, save it
            rval.append(ii)
    return rval


class ShibbolethPermissions(BasePlugin):
    """Extend folder_localrole_form to grant permissions to Shibboleth users.

    Most testing is done in tests/ShibbolethPermissions.txt."""
    security = ClassSecurityInfo()

    def __init__(self, pluginId, title=None):
        self.id = pluginId
        self.title = title
        self.localRoles = PersistentDict()
        self.retest = re.compile(' ')

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
        >>> from Products.ShibbolethPermissions.permissions import ShibbolethPermissions
        >>> ShibbolethPermissions('test').getLocalRoles()
        {}
        """
        logger.info("permissions.ShibbolethPermissions.getLocalRoles(%s, %s)" % (str(path), str(params)))
        roles = {}
        for ii in self.localRoles.iterkeys():
            roles[ii] = []
            for jj in self.localRoles[ii]:
                roles[ii].append(jj)
        if not path and not params:
            return roles        # no select given, so return everything
        if path:
            if not roles.has_key(path):
                return []       # path not found, so return nothing
            if not params:      # path found, but no subcriteria so return whole list
                return roles[path]
            return _searchParams(roles[path], params.keys().sort(), **params)
        # no path, but params, so return a path keyed dict of lists of dicts
        rval = {}
        for ii in roles.iterkeys(): # each key is a Plone path
            found = _searchParams(roles[ii], params.keys().sort(), **params)
            if found:           # Don't save empty lists
                rval[ii] = found
        return rval

    security.declarePublic('addLocalRoles')
    def addLocalRoles(self, path, params, roles):
        """Add a pattern for path of params."""
        logger.info("permissions.ShibbolethPermissions.addLocalRoles(%s, %s, %s)" % (str(path), str(params), str(roles)))
        params['_roles'] = roles
        if self.localRoles.has_key(path):
            self.localRoles[path].append(params)
        else:
            self.localRoles[path] = [params,]

    security.declarePublic('delLocalRoles')
    def delLocalRoles(self, path=None, row=None, **params):
        """Delete the specified roles."""
        logger.info("permissions.ShibbolethPermissions.delLocalRoles(%s, %s, %s)" % (str(path), str(row), str(params)))
        if not path:
            if not row and not params:
                self.localRoles.clear()
            return
        if not self.localRoles.has_key(path):
            logger.info("permissions.ShibbolethPermissions.delLocalRoles error: no path %s in localRoles" % str(path), exc_info=True)
            return
        if row:
            try:
                del self.localRoles[path][row]
            except (IndexError, TypeError):
                logger.warning("permissions.ShibbolethPermissions.delLocalRoles error deleting row %s from %s" % (str(row), str(path)), exc_info=True)
            return
        if params:
            paramKeys = params.keys().sort()
            delList = []
            index = -1
            for ii in self.localRoles[path]:
                index += 1
                if ii.keys().sort() != paramKeys:
                    continue    # both the subcriteria and source dictionary
                                # must have the same set of keys
                regexes = {}
                for jj in paramKeys:
                    regexes[jj] = re.compile(ii[jj])
                for jj in paramKeys:
                    found = regexes[jj].search(params[jj]) and True or False
                    if not found:
                        break   # This doesn't match, so no point in testing more
                if found:       # Got here as true, so it matched all, save it
                    delList.append(index)
            delList.reverse()
            for ii in delList:  # Delete them off of the end first
                del self.localRoles[path][ii]
            return
        del self.localRoles[path]

    security.declarePublic('updLocalRoles')
    def updLocalRoles(self, path=None, row=None, roles=[], **params):
        """Update the specified roles."""
        logger.info("permissions.ShibbolethPermissions.updLocalRoles(%s, %s, %s, %s)" % (str(path), str(row), str(roles), str(params)))
        if not path:
            return
        if not self.localRoles.has_key(path):
            logger.warning("permissions.ShibbolethPermissions.updLocalRoles error: no path %s in localRoles" % str(path), exc_info=True)
            return
        if row is not None:
            logger.info("permissions.ShibbolethPermissions.updLocalRoles setting localRoles[%s][%d]['_roles'] to %s" % (path, row, str(roles)))
            try:
                self.localRoles[path][row]['_roles'] = roles
            except (IndexError, TypeError):
                logger.warning("permissions.ShibbolethPermissions.updLocalRoles error updating row %s from %s" % (str(row), str(path)), exc_info=True)
            return
        if params:
            paramKeys = params.keys().sort()
            delList = []
            for ii in self.localRoles[path]:
                if ii.keys().sort() != paramKeys:
                    continue    # both the subcriteria and source dictionary
                                # must have the same set of keys
                regexes = {}
                for jj in paramKeys:
                    regexes[jj] = re.compile(ii[jj])
                for jj in paramKeys:
                    found = regexes[jj].search(params[jj]) and True or False
                    if not found:
                        break   # This doesn't match, so no point in testing more
                if found:       # Got here as true, so it matched all, save it
                    ii['_roles'] = roles

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

    security.declarePublic('listKeys')
    def listKeys(self, config):
        """Return sorted keys of config.

        This is a generic routing, so a simple test will do.
        >>> from Products.ShibbolethPermissions.permissions import ShibbolethPermissionsHandler
        >>> ShibbolethPermissionsHandler('test').listKeys({'b': 2, 'a': 1, 'c': 3})
        ['a', 'b', 'c']
        """
        logger.info("permissions.ShibbolethPermissionsHandler.listKeys(%s)" % repr(config))
        try:
            rval = config.keys()
        except (AttributeError, TypeError):
            return []
        rval.sort()
        return rval

    security.declarePublic('getShibAttrs')
    def getShibAttrs(self):
        """Return a list of (label, attribute) tupples."""
        autoUserMaker = getToolByName(self, 'AutoUserMakerPASPlugin')
        config = autoUserMaker.getSharingConfig()
        rval = []
        for ii in range(len(config['http_sharing_tokens'])):
            try:
                rval.append((config['http_sharing_labels'][ii],
                             config['http_sharing_tokens'][ii]))
            except IndexError:
                rval.append((config['http_sharing_tokens'][ii],
                             config['http_sharing_tokens'][ii]))
        return rval

    security.declareProtected(ManageUsers, 'manage_changeConfig')
    def manage_changeConfig(self, REQUEST=None):
        """Delete given paths."""
        if not REQUEST:
            return None
        for ii in REQUEST.form.get('plonepath', []):
            self.delLocalRoles(ii)
        return REQUEST.RESPONSE.redirect('%s/manage_config' % self.absolute_url())

InitializeClass(ShibbolethPermissionsHandler)
