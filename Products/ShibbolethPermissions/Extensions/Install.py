# This lets you install ShibbolethPermissions through Plone, if you're into that.
# If you aren't using Plone, it doesn't hurt anything.

import os

from App.Common import package_home
from HTMLParser import HTMLParser
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.PluggableAuthService.PluggableAuthService import logger
from Products.PythonScripts.PythonScript import PythonScript
from zExceptions import BadRequest

from Products.ShibbolethPermissions.permissions import ShibbolethPermissionsHandler
from Products.ShibbolethPermissions import shib_globals

scripts = ('shibattrs', 'shibperms', 'listkeys',
           'folder_localrole_shib_add', 'folder_localrole_shib_del',
           'folder_localrole_shib_upd')
EXTENSION_PROFILES = ('ShibbolethPermissions.policy:default',)

def _firstIdOfClass(container, class_):
    """Return the id of the first object of class `class_` within `container`.
    If there is none, return None."""
    for id in container.objectIds():
        if isinstance(container[id], class_):
            return id
    return None

def install(portal, reinstall=False):
    acl_users = getToolByName(portal, 'acl_users')

    # Put a ShibbolethPermisssion in the acl_users folder, if there isn't one:
    pluginId = _firstIdOfClass(acl_users, ShibbolethPermissionsHandler)
    if not pluginId:
        pluginId = 'ShibbolethPermissions'
        constructors = acl_users.manage_addProduct[pluginId]
        constructors.manage_addShibbolethPermissions(pluginId, title='ShibbolethPermissions Plugin')

    extensionsPath = os.path.join(package_home(shib_globals), 'Extensions')

    try:
        logger.info("checking for plone 3.0+")
        portal_kss = getToolByName(portal, 'portal_kss') # new in 3.0
        portal_setup = getToolByName(portal, 'portal_setup')
        portal_setup.runAllImportStepsFromProfile("profile-Products.ShibbolethPermissions:default", purge_old=False)
    except AttributeError: # getToolByName for portal_kss ends up here in 2.5
        # Update the folder_localrole_form
        logger.info("installing for plone 2.5")
        portal_skins = getToolByName(portal, 'portal_skins')
        try:
            if portal_skins.plone_forms.folder_localrole_form:
                logger.info("getting default folder_localrole_form")
                localrole = getattr(portal_skins.plone_forms, 'folder_localrole_form').document_src()
                logger.info("getting folder_localrole_form page template")
                zpt = open(os.path.join(extensionsPath, 'folder_localrole_form.zpt'))
                # edit folder_localrole_form.zpt to get the contents here
                logger.info("updating folder_localrole_form html")
                parser = MyHTMLParser('heading_advanced_settings', "".join(zpt.readlines()))
                zpt.close()
                parser.feed(localrole)
                parser.close()
                localrole = parser.getResult()
                localrole_form = ZopePageTemplate('folder_localrole_form', localrole)
                logger.info("saving updating folder_localrole_form to custom")
                portal_skins.custom._setObject('folder_localrole_form', localrole_form)
            else:
                raise "cannot find current folder_localrole_form in portal_skins.plone_forms"
        except Exception, err:
            logger.warning("error installing custom folder_localrole_form: %s" % str(err), exc_info=True)

        for script in scripts:
            logger.info("installing %s" % script)
            try:
                ploneScript = PythonScript(script)
                py = open(os.path.join(extensionsPath, script + '.py'))
                ploneScript.write("".join(py.readlines()))
                py.close()
                portal_skins.custom._setObject(script, ploneScript)
            except Exception, err:
                logger.warning(str(err), exc_info=True)

    # Now restore the configuration
    if reinstall:
        import pickle
        plugin = getattr(acl_users.plugins, pluginId)
        # Get the configuration out of the property, and delete the property.
        try:
            prop = "\n".join(acl_users.getProperty('sp_config'))
            logger.info("sp_config = %s" % repr(prop))
            config = pickle.loads(prop)
        except Exception, err:
            logger.warning("error getting config: %s of %r" % (str(err), repr(err)), exc_info=True)
        roles = acl_users.portal_role_manager.listRoleIds()
        logger.info("roles = %s" % str(roles))
        for path in config.iterkeys():
            for entry in config[path]:
                thisRole = []
                for role in entry['_roles']:
                    logger.info("role = %s" % role)
                    if role in roles:
                        thisRole.append(role)
                thisParam = entry
                del thisParam['_roles']
                logger.info("pathj = %s, attrs = %s, roles = %s" % (path, str(thisParam), str(thisRole)))
                plugin.addLocalRoles(path, thisParam, thisRole)
    try:
        acl_users.manage_delProperties(['sp_config'])
    except:
        pass

def uninstall(portal, reinstall=False):
    acl_users = getToolByName(portal, 'acl_users')
    pluginId = _firstIdOfClass(acl_users, ShibbolethPermissionsHandler)
    try:
        portal_kss = getToolByName(portal, 'portal_kss') # new in 3.0
        ver=3.0
    except AttributeError:
        ver=2.5
    if pluginId:
        if reinstall:
            import pickle
            plugin = getattr(acl_users.plugins, pluginId)
            config = plugin.getLocalRoles()
            conf = pickle.dumps(config)
            logger.info("sp_config = %s" % repr(conf))
            acl_users.manage_addProperty(id='sp_config', type='lines', value=conf)
        acl_users.manage_delObjects(ids=[pluginId])  # implicitly deactivates
        portal_skins = getToolByName(portal, 'portal_skins')
        for ii in ('folder_localrole_form',) + scripts:
            try:
                portal_skins.custom.manage_delObjects([ii])
            except Exception, err:
                if ver == 2.5:
                    logger.warning(str(err), exc_info=True)


class MyHTMLParser(HTMLParser): #IGNORE:R0904
    """Pass all through, adding the given form, when the given pattern matches.

    In Plone 2.5, find 'heading_advanced_settings' and insert the Shib form."""
    from htmlentitydefs import entitydefs

    tSingles = ('br', 'img', 'input', 'hr')

    def __init__(self, sPattern, sForm):
        """Set up output holders and state variables, and initialize parser."""
        self.lOutput = list()
        self._initVars()
        HTMLParser.__init__(self)
        self.sPattern = sPattern
        self.sForm = sForm

    def _initVars(self):
        """Set/reset variables used to track mailto URLs."""
        self.bEmail = False
        self.sEncoded = ''
        self.sVisible = ''
        self.sAttrs = ''

    def handle_starttag(self, sTag, lAttrs):
        """Pass through all start tags, except anchors of mailto urls."""
        lTemp = list()
        sMailto = ''
        for sKey, sVal in lAttrs:
            if sVal == self.sPattern:
                self.lOutput.append(self.sForm)
            lTemp.append('%s="%s"' % (sKey, sVal))
        if len(lTemp) == 0:
            if sTag in (self.tSingles):
                self.lOutput.append("<%s />" % sTag)
            else:
                self.lOutput.append("<%s>" % (sTag))
        else:
            if sTag in (self.tSingles):
                self.lOutput.append("<%s %s />" % (sTag, ' '.join(lTemp)))
            else:
                self.lOutput.append("<%s %s>" % (sTag, ' '.join(lTemp)))

    def handle_endtag(self, sTag):
        "Record when exiting a sought after tag."
        if sTag in self.tSingles:
            return
        self.lOutput.append("</%s>" % (sTag))

    def handle_data(self, sData):
        """Save the data found."""
        self.lOutput.append(sData)

    def handle_charref(self, sData):
        """Pass character references through."""
        self.lOutput.append('&#%s;' % sData)

    def handle_entityref(self, sData):
        """Pass entity references through."""
        if self.entitydefs.has_key(sData):
            self.lOutput.append("&%s;" % (sData))
        else:
            # From Plone: this breaks non-standard entities that end with ';'
            self.lOutput.append("&%s" % (sData))

    def handle_comment(self, sData):
        """Pass comments through."""
        self.lOutput.append("<!--%s-->" % sData)

    def handle_decl(self, sData):
        """Pass declarations through."""
        self.lOutput.append("<!%s>" % sData)

    def getResult(self):
        """Return any available HTML."""
        sTemp = ''.join(self.lOutput)
        #Remove the
        self.lOutput = list()
        return sTemp
