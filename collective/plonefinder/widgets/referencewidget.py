from zope.schema.interfaces import InvalidValue
from Acquisition import aq_inner
from zope.app.form.browser import OrderedMultiSelectWidget
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.plonefinder import siteMessageFactory as _
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName


class FinderSelectWidget(OrderedMultiSelectWidget) :
    """
    A base widget with a plone_finder link
    for a Sequence field (tuple or list)
    that could reference any kind of value
    from browsed objects
    By defaut uid is used as value
    """
    
    template = ViewPageTemplateFile('finderbase.pt')
    finderlabel = _(u'Browse for contents') 
    moveuplabel = _(u'Move up')
    movedownlabel = _(u'Move down')
    deleteentrylabel = _(u'Remove item')
    types = []
    typeview = 'file'
    query = None
    selectiontype = 'uid'
    allowupload = 0
    allowaddfolder = 0
    allowimagesizeselection = 0
                
    def __init__(self, field, request):
        """
        TODO : set some plone_finder attributes in session
        for a smaller querystring
        The most important improvement can be the plone_finder blacklist stored in session
        to remove selected objects from plone_finder results
        """
        if field.value_type != None :
            voc = field.value_type.vocabulary
        else :
            voc = None
        super(FinderSelectWidget, self).__init__(field, voc, request)
    
    def _getBase(self) :
        if hasattr(self.context.context, self.context.__name__):
            return aq_inner(aq_inner(self.context).context)
        else :
            return getSite()
    
    def getTitleFromValue(self, value) :
        base = self._getBase()
        reference_tool = getToolByName(base, 'reference_catalog')
        # the value could be
        # uid or uid/image_thumb or uid/view or uid/download ....
        uid = value.split('/')[0]
        obj = reference_tool.lookupObject(uid)
        if obj is not None :
            return obj.pretty_title_or_id()
        else :
            raise InvalidValue("uid %s not found in reference tool" % value)

    def finderlink(self) :
        """
        return the finder link
        """
        base = self._getBase()
        # TODO : put all these queryString pairs in session (see finder.py)
        finderquery = 'fieldid=%s&fieldname=%s&typeview=%s&selectiontype=%s&allowupload:int=%i&allowaddfolder:int=%i&allowimagesizeselection:int=%i'\
                      %(self.name, self.name, self.typeview, self.selectiontype, int(self.allowupload), int(self.allowaddfolder), int(self.allowimagesizeselection))
        for typeId in self.types :
            finderquery += '&types:list=%s' %typeId.replace(' ', '+')
        return "openFinder('%s/@@plone_finder?%s')" %(base.absolute_url(),finderquery)

    def convertTokensToValues(self, tokens):
        """Convert term tokens to the terms themselves.
        if vocabulary is None just append token in values list
        """
        values = []
        for token in tokens:
            if self.vocabulary is not None :
                try:
                    term = self.vocabulary.getTermByToken(token)
                except LookupError, error:
                    raise InvalidValue("token %r not found in vocabulary" % token)
                else:
                    values.append(term.value)
            else :
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

        if self.vocabulary is not None :
            terms = [self.vocabulary.getTerm(value)
                     for value in values]
            return [{'text': self.textForValue(term), 'value': term.token}
                    for term in terms]
        elif self.selectiontype == 'uid' :
            return [{'text': self.getTitleFromValue(value), 'value': value}
                    for value in values]        
        else :
            return [{'text': value, 'value': value}
                    for value in values]

"""
Some examples for customized widgets
but you can also just use FinderSelectWidget
with specific attributes
"""

class FinderSelectFileWidget(FinderSelectWidget) :
    """
    A widget with a plone_finder link
    for a Sequence field (tuple or list)
    that could reference and upload files
    """
    finderlabel = _(u'Browse for files') 
    types = ['File']
    allowupload = 1
    allowaddfolder = 1

class FinderSelectImageWidget(FinderSelectWidget) :
    """
    A widget with a plone_finder link
    for a Sequence field (tuple or list)
    that could reference and upload images
    values are stored as uid/image_size
    """
    finderlabel = _(u'Browse for images') 
    types = ['Image', 'News Item']
    typeview = 'image'
    allowupload = 1
    allowaddfolder = 1
    allowimagesizeselection = 1

