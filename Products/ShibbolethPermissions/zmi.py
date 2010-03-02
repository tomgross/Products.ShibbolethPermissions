"""Used in installing ShibbolethPermissions."""

__revision__ = '0.1'

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.ShibbolethPermissions.permissions import ShibbolethPermissionsHandler

manage_addShibbolethPermissionsForm = PageTemplateFile('add-ShibbolethPermissions.zpt', globals())

def manage_addShibbolethPermissions(self, pluginId, title='', REQUEST=None):
    """Add giving permissions to a Shibboleth user."""

    handler = ShibbolethPermissionsHandler(pluginId, title)
    self._setObject(handler.getId(), handler)

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect('%s/manage_workspace'
                                     '?manage_tabs_message='
                                     'ShibbolethPermissions+added.'
                                     % self.absolute_url())
