# -*- coding: utf-8 -*-
# $Id$
"""Public widget"""

from zope.schema.interfaces import InvalidValue
from ZTUtils import make_query
from zope.app.form.browser import OrderedMultiSelectWidget
from zope.formlib.widgets import TextWidget
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

from collective.plonefinder import siteMessageFactory as _


def absolute_image_url(context, value):
    portal_state = context.restrictedTraverse('@@plone_portal_state')
    portal_url = portal_state.portal_url()
    return portal_url + '/resolveuid/' + value


class FinderImageWidget(TextWidget):
    """A base widget with a plone_finder link for a Sequence field (tuple or
    list) that could reference any kind of value from browsed objects By defaut
    uid is used as value
    """
    template = ViewPageTemplateFile('finderimage.pt')
    finderlabel = _(u'Browse for image')
    types = ['Image']
    typeview = 'image'
    imagestypes = ('Image',)
    query = None
    selectiontype = 'uid'
    allowupload = False
    allowaddfolder = False
    allowimagesizeselection = True
    forcecloseoninsert = True
    base = None

    def __call__(self):
        self.value = self._getFormValue()
        if self.value is None or self.value == self.context.missing_value:
            self.value = ''
        return self.template()

    def _getBaseUrl(self):
        base = getSite()
        return base.absolute_url()

    def htmlid(self):
        return self.name.replace('.', '_')

    def portal_url(self):
        content = self.context.context
        portal_state = content.restrictedTraverse('@@plone_portal_state')
        portal_url = portal_state.portal_url()
        return portal_url

    def image_url(self):
        return absolute_image_url(self.context.context, self.value)

    def finder_url(self):
        """JS link that opens the finder
        """
        base_url = self._getBaseUrl()
        # TODO: put all these queryString pairs in session (see finder.py)
        values = {
            'fieldid': self.htmlid(),
            'fieldname': self.htmlid(),
            'typeview': self.typeview,
            'selectiontype': self.selectiontype,
            'allowupload': int(self.allowupload),
            'allowaddfolder': int(self.allowaddfolder),
            'allowimagesizeselection': int(self.allowimagesizeselection),
            'forcecloseoninsert': int(self.forcecloseoninsert),
            'types': list(self.types),
            'imagestypes': list(self.imagestypes)
            }
        return '%s/@@plone_finder?%s' % (base_url, make_query(values))


class FinderSelectWidget(OrderedMultiSelectWidget):
    """A base widget with a plone_finder link for a Sequence field (tuple or
    list) that could reference any kind of value from browsed objects By defaut
    uid is used as value
    """
    template = ViewPageTemplateFile('finderbase.pt')
    finderlabel = _(u'Browse for contents')
    moveuplabel = _(u'Move up')
    movedownlabel = _(u'Move down')
    deleteentrylabel = _(u'Remove item')
    types = ()
    typeview = 'file'
    imagestypes = ('Image', 'News Item')
    query = None
    selectiontype = 'uid'
    allowupload = False
    allowaddfolder = False
    allowimagesizeselection = False
    forcecloseoninsert = False
    base = None


    def __init__(self, field, request):
        """TODO: set some plone_finder attributes in session for a smaller
        querystring. The most important improvement can be the plone_finder
        blacklist stored in session to remove selected objects from plone_finder
        results
        """
        if field.value_type != None:
            voc = field.value_type.vocabulary
        else:
            voc = None
        if self.base is None:
            self.base = getSite()
        super(FinderSelectWidget, self).__init__(field, voc, request)


    def _getBaseUrl(self):
        return self.base.absolute_url()


    def getTitleFromValue(self, value):
        reference_tool = getToolByName(self.base, 'reference_catalog')
        pm = getToolByName(self.base, 'portal_membership')
        # the value could be
        # uid or uid/image_thumb or uid/view or uid/download ....
        uid = value.split('/')[0]
        obj = reference_tool.lookupObject(uid)
        if obj is not None:
            if pm.checkPermission('View', obj):
                return obj.pretty_title_or_id()
            return '%s : %s ' %(_(u"You don't have permission to access this object"),uid)
        else:
            return '%s : %s ' %(_(u"Object not found with uid"),uid)


    def finderlink(self):
        """JS link that opens the finder
        """
        base_url = self._getBaseUrl()
        # TODO: put all these queryString pairs in session (see finder.py)
        values = {
            'fieldid': self.name,
            'fieldname': self.name,
            'typeview': self.typeview,
            'selectiontype': self.selectiontype,
            'allowupload': int(self.allowupload),
            'allowaddfolder': int(self.allowaddfolder),
            'allowimagesizeselection': int(self.allowimagesizeselection),
            'forcecloseoninsert': int(self.forcecloseoninsert),
            'types': list(self.types),
            'imagestypes': list(self.imagestypes)
            }
        return "openFinder('%s/@@plone_finder?%s')" % (base_url, make_query(values))


    def convertTokensToValues(self, tokens):
        """Convert term tokens to the terms themselves.
        if vocabulary is None just append token in values list
        """
        values = []
        for token in tokens:
            if self.vocabulary is not None:
                try:
                    term = self.vocabulary.getTermByToken(token)
                except LookupError:
                    raise InvalidValue("token %r not found in vocabulary" % token)
                else:
                    values.append(term.value)
            else:
                values.append(token)
        return values


    def selected(self):
        """Return a list of tuples (text, value) that are selected
           when vocabulary is not None
           otherwise return list of tuples (value, value)."""

        # Get form values
        values = self._getFormValue()
        # Not all content objects must necessarily support the attributes
        if hasattr(self.context.context, self.context.__name__):
            # merge in values from content
            for value in self.context.get(self.context.context):
                if value not in values:
                    values.append(value)

        if self.vocabulary is not None:
            terms = [self.vocabulary.getTerm(value)
                     for value in values]
            return [{'text': self.textForValue(term), 'value': term.token}
                    for term in terms]
        elif self.selectiontype == 'uid':
            return [{'text': self.getTitleFromValue(value), 'value': value}
                    for value in values]
        else:
            return [{'text': value, 'value': value}
                    for value in values]

# Some examples for customized widgets but you can also just use
# FinderSelectWidget with specific attributes

class FinderSelectFileWidget(FinderSelectWidget):
    """A widget with a plone_finder link for a Sequence field (tuple or list)
    that could reference and upload files
    """
    finderlabel = _(u'Browse for files')
    types = ['File']
    allowupload = 1
    allowaddfolder = 1


class FinderSelectImageWidget(FinderSelectWidget):
    """A widget with a plone_finder link for a Sequence field (tuple or list)
    that could reference and upload images values are stored as uid/image_size
    """
    finderlabel = _(u'Browse for images')
    types = ['Image', 'News Item']
    typeview = 'image'
    allowupload = 1
    allowaddfolder = 1
    allowimagesizeselection = 1

