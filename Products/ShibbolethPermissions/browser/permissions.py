import zope.component

from persistent.dict import PersistentDict

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PluggableAuthService.PluggableAuthService import logger
from plone.app.workflow.interfaces import ISharingPageRole
from zExceptions import Forbidden

from plone.memoize.view import memoize

def _getList(form, value):
    """ Return a list regardless of single input value or list."""
    rval = form.get(value, [])
    if not isinstance(rval, list):
        rval = [rval,]
    return rval

class ShibbolethView(BrowserView):
    """"""

    template = ViewPageTemplateFile('shibboleth.pt')

    def __call__(self):
        """"""
        postback = True
        form = self.request.form
        submitted = form.get('form.submitted', False)
        update_button = form.get('form.button.Update', None) is not None
        save_button   = form.get('form.button.Save', None) is not None
        cancel_button = form.get('form.button.Cancel', None) is not None
        if submitted and not cancel_button:
            if not self.request.get('REQUEST_METHOD','GET') == 'POST':
                raise Forbidden
            path = form.get('physicalPath', None)
            if not path:
                raise Forbidden
            if save_button:
                self.save(path)
            else:
                self.update(path)

        # Other buttons return to the sharing page
        if cancel_button:
            postback = False
        if postback:
            return self.template()
        else:
            context_state = zope.component.getMultiAdapter(
                (self.context, self.request), name="plone_context_state")
            url = context_state.view_url()
            self.request.response.redirect(url)

    def save(self, path):
        form = self.request.form
        attribs = _getList(form, 'add_attribs')
        values = _getList(form, 'add_values')
        member_role = _getList(form, 'add_member_role')
        shibattr = PersistentDict([(attrib, values[ii])
                         for ii, attrib in enumerate(attribs) if values[ii]])
        if shibattr and member_role:
            self.shibpermsplugin().addLocalRoles(path, shibattr, member_role)

    def update(self, path):
        form = self.request.form
        row_number = _getList(form, 'row_number')
        row_number.sort(reverse=True)
        if form.get('form.button.Delete', None) is not None:
            for ii in row_number:
                if ii:
                    self.shibpermsplugin().delLocalRoles(path, int(ii))
        else:
            member_role = _getList(form, 'upd_member_role')
            for ii in row_number:
                if ii:
                    self.shibpermsplugin().updLocalRoles(path,
                                                         int(ii),
                                                         member_role)

    @memoize
    def roles(self):
        """Get a list of roles that can be managed.

        Returns a list of dics with keys:

        	- id
        	- title
        """
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        pairs = [
            {'id': name, 'title': utility.title}
            for name, utility in zope.component.getUtilitiesFor(ISharingPageRole)
            if utility.required_permission is None or \
                    mtool.checkPermission(utility.required_permission, context)]
        pairs.sort(lambda x, y: cmp(x['id'], y['id']))
        return pairs

    @memoize
    def shibpermsplugin(self):
        context = aq_inner(self.context)
        acl_users = getToolByName(context, 'acl_users')
        return acl_users['ShibbolethPermissions']

    def shibattrs(self):
        """
        """
        return self.shibpermsplugin().getShibAttrs()

    def shibperms(self):
        """
        """
        path = '/'.join(self.context.getPhysicalPath())
        return self.shibpermsplugin().getLocalRoles(path)

    def listkeys(self, config):
        """
        """
        return self.shibpermsplugin().listKeys(config)
