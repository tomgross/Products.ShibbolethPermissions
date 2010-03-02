from Acquisition import aq_inner, aq_base
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PluggableAuthService.PluggableAuthService import logger
from plone.app.workflow.interfaces import ISharingPageRole
from zExceptions import Forbidden
from zope.component import getUtilitiesFor

from plone.memoize.instance import memoize, clearafter

def _getList(form, value):
	"""Return a list regardless of single input value or list."""
	rval = form.get(value, [])
	if not isinstance(rval, list):
		rval = [rval,]
	logger.info("permissions.ShibbolethView %s = %s" % (value, str(rval)))
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
		logger.info("permissions.ShibbolethView update = %s" % str(update_button))
		delete_button = form.get('form.button.Delete', None) is not None
		logger.info("permissions.ShibbolethView delete = %s" % str(delete_button))
		save_button   = form.get('form.button.Save',   None) is not None
		logger.info("permissions.ShibbolethView save = %s" % str(save_button))
		cancel_button = form.get('form.button.Cancel', None) is not None
		logger.info("permissions.ShibbolethView cancel = %s" % str(cancel_button))
		if submitted and not cancel_button:
			if not self.request.get('REQUEST_METHOD','GET') == 'POST':
				raise Forbidden
			path = form.get('physicalPath', None)
			if not path:
				raise Forbidden
			logger.info("permissions.ShibbolethView path = %s" % str(path))
			acl_users = getToolByName(self, 'acl_users')
			if save_button:
				attribs = _getList(form, 'add_attribs')
				values = _getList(form, 'add_values')
				member_role = _getList(form, 'add_member_role')
				shibattr = {}
				for ii in range(len(attribs)):
					try:
						if values[ii]:
							shibattr[attribs[ii]] = values[ii]
					except IndexError:
						break
				if shibattr and member_role:
					acl_users.ShibbolethPermissions.addLocalRoles(path, shibattr, member_role)
			else:
				row_number = _getList(form, 'row_number')
				if delete_button:
					row_number.sort(reverse=True)
					for ii in row_number:
						logger.info("permissions.ShibbolethView trying to delete row %s" % str(ii))
						try:
							if ii:
								acl_users.ShibbolethPermissions.delLocalRoles(path, int(ii))
						except (TypeError, IndexError):
							pass
				else:
					member_role = _getList(form, 'upd_member_role')
					row_number.sort(reverse=True)
					for ii in row_number:
						logger.info("permissions.ShibbolethView trying to update row %s" % str(ii))
						try:
							if ii:
								acl_users.ShibbolethPermissions.updLocalRoles(path, int(ii), member_role)
						except (TypeError, IndexError):
							pass
		# Other buttons return to the sharing page
		if cancel_button:
			postback = False
		if postback:
			return self.template()
		else:
			context_state = self.context.restrictedTraverse("@@plone_context_state")
			url = context_state.view_url()
			self.request.response.redirect(url)

	@memoize
	def roles(self):
		"""Get a list of roles that can be managed.

		Returns a list of dics with keys:

			- id
			- title
		"""
		context = aq_inner(self.context)
		portal_membership = getToolByName(context, 'portal_membership')
		pairs = []
		for name, utility in getUtilitiesFor(ISharingPageRole):
			permission = utility.required_permission
			if permission is None or portal_membership.checkPermission(permission, context):
				pairs.append(dict(id = name, title = utility.title))
		pairs.sort(lambda x, y: cmp(x['id'], y['id']))
		return pairs

	def shibattrs(self):
		"""
		"""
		logger.info("permissions.ShibbolethView.shibattrs()")
		acl_users = getToolByName(self, 'acl_users')
		return acl_users.ShibbolethPermissions.getShibAttrs()

	def shibperms(self, where):
		"""
		"""
		logger.info("permissions.ShibbolethView.shibperms()")
		acl_users = getToolByName(self, 'acl_users')
		return acl_users.ShibbolethPermissions.getLocalRoles('/'.join(where.getPhysicalPath()))

	def listkeys(self, config):
		"""
		"""
		logger.info("permissions.ShibbolethView.listkeys(%r)" % config)
		try:
			rval = config.keys()
		except (AttributeError, TypeError):
			return []
		rval.sort()
		return rval
