# -*- coding: utf-8 -*-
# $Id$
"""Finder pop up control"""

from ZTUtils import make_query
from zope.interface import implements

from Products.Five import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.ATContentTypes.interface import IATTopic

from collective.plonefinder.interfaces import IFinder
from interfaces import IFinderUploadCapable
from collective.plonefinder import siteMessageFactory as _
from collective.plonefinder.utils import pleaseDontCache


try:
    from plone.app.contenttypes.interfaces import IImage
    HAS_PAC = True
except ImportError:
    HAS_PAC = False

def _quotestring(s):
    return '"%s"' % s

def _quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, _quotestring(char))
    return s


def isPlone3():
    return getFSVersionTuple()[0] == 3


def getPathClass(browsedpath, currentpath):
    """
    if currentpath == browsedpath return ' currentitem'
    if currentpath is parent of browsedpath return ' currentnode'
    else return ''
    """

    if currentpath==browsedpath:
        return ' currentitem'
    else:
        browsedpathList = browsedpath.split('/')
        currentpathList = currentpath.split('/')
        if len(browsedpathList) > len(currentpathList):
            isCurrentNode = True
            for index, id in enumerate(currentpathList):
                if id != browsedpathList[index]:
                    isCurrentNode = False
                    break
            if isCurrentNode:
                return ' currentnode'
    return ''


def finderTopicsQueryCatalog(scope, catalog,  **kw):
    """Redefine the queryCatlog method defined in AT Topics to allow a query
    override with kw args and to return 0 results when there are no criteria
    inside topic (other use cases are not interesting here)
    """

    query = scope.buildQuery()
    if query is None:
        return []
    else:
        # Allow parameters to override existing criterias
        query.update(kw)
        return catalog(**query)

FORM_PARAMS = ('SearchableText',)


class Finder(BrowserView):
    """Class for Plone Finder View
    """
    implements(IFinder)

    template = ViewPageTemplateFile('finder.pt')

    def __init__(self, context, request):
        super(Finder, self).__init__(context, request)
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        # dict to place persistent objects
        self.data = {
            'portal': portal,
            'root': None,
            'scope': None,
            'catalog': getToolByName(portal, 'portal_catalog')
            }
        self.is_plone3 = isPlone3()
        self.portal_url = portal_url()
        self.portalpath = '/'.join(portal.getPhysicalPath())
        self.breadcrumbs = []
        # All these properties could be overloaded in a Finder's inherited class
        self.findername = 'plone_finder'
        #: Visible breadcrumbs in finder
        self.showbreadcrumbs = True
        self.scopetitle = ''
        self.scopetype = ''
        self.scopeiconclass = 'divicon'
        #: Select multiple elements
        self.multiselect = True
        #: Closes the finder on selecting an item
        self.forcecloseoninsert = 0
        #: Browsing root path
        self.rootpath = ''
        self.browsedpath = ''
        self.parentpath = ''
        self.types = []
        #: View of types in content panel of finder. 'file', 'image' or 'selection'
        self.typeview = 'file'
        self.typecss = 'list'
        #: Enable browsing
        self.browse = True
        self.sort_on = 'getObjPositionInParent'
        self.sort_order = ''
        self.sort_inverse = 'ascending'
        self.sort_request = False
        self.sort_withcatalog = True
        #: ???
        self.displaywithoutquery = True
        #: uids of items to be hidden (thus not selectable)
        self.blacklist = []
        self.addtoblacklist = []
        self.removefromblacklist = []
        #: Mapping of catalog query keyword arguments or None
        self.query = None
        # FIXME: We should use an interface instead (IATImage ?)
        #: Portal types that may show image vignetes
        self.imagestypes = ('Image', )
        # FIXME: We should use an interface instead (IIcon ?)
        #: Portal types that may have specific icons
        self.filestypes = ('File',)
        #: Type of returned value, may be 'uid' or 'url'
        self.selectiontype = 'uid'
        #: Do we enable selecting specific image size variants of IATImage items?
        self.allowimagesizeselection = True
        #: Id of the field that has this finder widget
        self.fieldid = 'demofield'
        #: Name of the field that has this finder widget
        self.fieldname = 'demofield'
        #: Type of the field that has this finder widget (FIXME: seems useless)
        self.fieldtype = 'list'
        #: True to show the finder in browser popup, Flase for an Ajax style overlay
        self.ispopup = True
        #: True to show anyway blacklisted items (but these are not selectable)
        self.showblacklisted = True
        #: True to display the search box
        self.showsearchbox = True
        #: True to display search results
        self.searchsubmit = False
        #: True to allow file upload through the finder
        self.allowupload = False
        #: True to display upload widget by default, only relevant if self.allowupload = True
        self.openuploadwidgetdefault = False
        #: True to allow creating new folders through the finder
        self.allowaddfolder = False
        #: Portal type built to hold object upload through finder UI
        self.typeupload = ''
        #: Portal type built when creating folder through finder UI
        self.typefolder = ''
        # Change this property
        # to define your own methods (overload selectItem as example)
        self.jsaddons = ''
        # Change this property to define your own css
        self.cssaddons = ''


    def __call__(self):
        """Called on view being published
        """
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        session = request.get('SESSION', {})

        pleaseDontCache(context, request)

        # Updating attributes from request values
        for name in (
            'rootpath', 'browse', 'showbreadcrumbs', 'multiselect',
            'forcecloseoninsert', 'types', 'typeupload', 'typefolder',
            'typeview', 'displaywithoutquery', 'query', 'imagestypes',
            'filestypes', 'selectiontype', 'allowimagesizeselection', 'fieldid',
            'fieldname', 'fieldtype', 'ispopup', 'showblacklisted',
            'searchsubmit', 'allowupload', 'allowaddfolder'
            ):
            setattr(self, name, request.get(name, getattr(self, name)))

        if not self.browse:
            self.showbreadcrumbs = False

        self.setScopeInfos(context, request, self.showbreadcrumbs)

        if not self.multiselect:
            self.forcecloseoninsert = 1

        if self.typeview == 'image':
            self.typecss = 'float'

        if request.get('finder_sort_on'):
            self.sort_on = request.get('finder_sort_on')
            self.sort_order = request.get('sort_order', self.sort_order)

            # sort_order could be empty or reverse, or ascending
            if self.sort_order=='reverse':
                self.sort_inverse = 'ascending'
            elif self.sort_order=='ascending':
                self.sort_inverse = 'reverse'
            self.sort_request = True
            if self.sort_on not in self.data['catalog'].indexes():
                self.sort_withcatalog = False

        # Use self.blacklist (or blacklist in session or request) to remove some
        # uids from results
        rblacklist = request.get('blacklist', self.blacklist)
        sblacklist = session.get('blacklist', rblacklist)
        if sblacklist and not rblacklist and not request.get('newsession', False):
            self.blacklist = sblacklist
        else:
            self.blacklist = rblacklist

        # Use self.addtoblacklist (or addtoblacklist in request) to add elements
        # in blacklist
        addtoblacklist = request.get('addtoblacklist', self.addtoblacklist)
        for k in addtoblacklist:
            if k not in self.blacklist:
                self.blacklist.append(k)

        # Use self.removefromblacklist (or removefromblacklist in request) to
        # remove elements from blacklist
        removefromblacklist = request.get('removefromblacklist', self.removefromblacklist)
        for k in removefromblacklist:
            if k in self.blacklist:
                self.blacklist.remove(k)

        # Put new blacklist in session
        # FIXME: KISS
        if session:
            if request.get('emptyblacklist', False):
                session.set('blacklist', [])
            else:
                session.set('blacklist', self.blacklist)

        firstpassresults = self.finderResults()
        if self.sort_request and not self.sort_withcatalog:
            firstpassresults.sort(key=lambda k: k[self.sort_on])
            if self.sort_order == 'reverse':
                firstpassresults.reverse()

        # remove blacklisted uids or just set it as blacklisted if needed
        results = []

        if self.selectiontype == 'uid':
            for r in firstpassresults:
                if r['uid'] not in self.blacklist or self.typeview=='selection':
                    results.append(r)
                elif self.showblacklisted:
                    r['blacklisted'] = True
                    results.append(r)

        self.results = results
        self.folders = []
        self.rootfolders = []
        if self.browse:
            self.folders = self.finderBrowsingResults()
            if self.data['scope'] is self.data['root']:
                self.rootfolders = self.folders
            else:
                self.rootfolders = self.finderNavBrowsingResults()

        self.cleanrequest = self.cleanRequest()

        # Upload disallowed if user do not have permission to Add portal content
        # on main window context
        if self.allowupload:
            tool = getToolByName(context, "portal_membership")
            if not(tool.checkPermission('Add portal content', self.data['scope'])):
                self.allowupload = False
            if not IFinderUploadCapable.providedBy(self.data['scope']):
                self.allowupload = False

        # Allowaddfolder disallowed if user do not have permission to add portal
        # content on context disallowed also when context is not
        # IFinderUploadCapable
        # FIXME: This should require allowupload otherwise this has no sense
        if self.allowaddfolder:
            tool = getToolByName(context, "portal_membership")
            if not(tool.checkPermission('Add portal content', self.data['scope'])):
                self.allowaddfolder = False
            if not IFinderUploadCapable.providedBy(self.data['scope']):
                self.allowaddfolder = False

        self.cleanrequest = self.cleanRequest()

        return self.template()


    def setScopeInfos(self, context, request, showbreadcrumbs):
        """Set scope and all infos related to scope
        """
        browsedpath = request.get('browsedpath', self.browsedpath)
        portal = self.data['portal']

        # Find browser root and rootpath if undefined
        if self.data['root'] is None:
            self.data['root'] = root = aq_inner(
                portal.restrictedTraverse(self.rootpath)
            )
            if not self.rootpath:
                self.rootpath = '/'.join(root.getPhysicalPath())

        # Find scope if undefined. By default scope = browsedpath or first
        # parent folderish or context if context is a folder
        scope = self.data['scope']
        if scope is None:
            if browsedpath:
                self.data['scope'] = scope = aq_inner(portal.restrictedTraverse(browsedpath))
            else:
                folder = aq_inner(context)
                if not bool(getattr(aq_base(folder), 'isPrincipiaFolderish', False)):
                    folder = aq_inner(folder.aq_parent)
                    while "portal_factory" in folder.getPhysicalPath():
                        folder = aq_inner(folder.aq_parent)
                self.data['scope'] = scope = folder

        self.scopetitle = scope.pretty_title_or_id()
        self.scopetype = scopetype = scope.portal_type
        self.scopeiconclass = 'contenttype-%s divicon' % scopetype.lower().replace(' ','-')

        # set browsedpath and browsed_url
        self.browsedpath = '/'.join(scope.getPhysicalPath())
        self.browsed_url = scope.absolute_url()
        if scope is not self.data['root']:
            parentscope = aq_inner(scope.aq_parent)
            self.parentpath = '/'.join(parentscope.getPhysicalPath())

        # set breadcrumbs
        # TODO: use self.data['catalog']
        portal_membership = getToolByName(context, "portal_membership")
        if showbreadcrumbs:
            crumbs = []
            item = scope
            itempath = self.browsedpath
            while itempath != self.rootpath:
                crumb = {}
                crumb['path'] = itempath
                crumb['title'] = item.title_or_id()
                crumb['show_link'] = portal_membership.checkPermission('View', item)
                crumbs.append(crumb)
                item = aq_inner(item.aq_parent)
                itempath = '/'.join(item.getPhysicalPath())
            crumbs.reverse()
            self.breadcrumbs = crumbs


    def finderQuery(self, topicQuery=None):
        """Query for results depending on some params
        """
        request = self.request
        if self.query:
            return self.query
        elif self.typeview == 'selection':
            return {'uid': self.blacklist}
        elif self.displaywithoutquery or self.searchsubmit:
            query = {}
            path = {}
            if not self.searchsubmit:
                path['depth'] = 1
            path['query'] =  self.browsedpath
            query['path'] = path
            sort_index = self.sort_on
            if self.sort_withcatalog:
                query['sort_on'] = sort_index
                query['sort_order'] = self.sort_order
            if self.types:
                query['portal_type'] = self.types

            if self.searchsubmit:
                # TODO: use a dynamic form with different possible searchform fields
                q = request.get('SearchableText', '')
                if q:
                    for char in '?-+*':
                        q = q.replace(char, ' ')
                    r=q.split()
                    r = " AND ".join(r)
                    searchterms = _quote_bad_chars(r)+'*'

                    query['SearchableText'] = searchterms

            return query

    def finderNavBrowsingResults(self, querypath=''):
        """Left navigation subtree results
        """
        if not querypath:
            querypath = self.rootpath
        return self.finderBrowsingResults(querypath=querypath, isnav=True)


    def finderBrowsingQuery(self, querypath=None):
        """Return query for folderishs to browse
        """
        if self.browse:
            path = {'depth': 1}
            if querypath:
                path['query'] = querypath
            else:
                path['query'] = self.browsedpath
            return {
                'path': path,
                'is_folderish': True,
                'sort_on': 'getObjPositionInParent'
                }


    def finderBrowsingResults(self, querypath=None, isnav=False):
        """Return results to browse method used for finder left navigation and
        navigation inside main window
        """
        cat = self.data['catalog']
        query = self.finderBrowsingQuery(querypath)
        brains = cat(**query)
        results = []
        for b in brains:
            r = {}
            r['uid'] = b.UID
            r['url'] = b.getURL()
            r['title'] = b.pretty_title_or_id()
            r['jstitle'] = r['title'].replace("\x27", "\x5C\x27")
            r['description'] = b.Description
            r['iconclass'] = 'contenttype-%s divicon' % b.portal_type.lower().replace(' ','-')
            r['type'] = b.portal_type
            r['path'] = b.getPath()
            r['state_class'] = 'state-%s' % b.review_state
            r['path_class'] = ''
            r['sub_folders'] = []
            if isnav:
                r['path_class'] = getPathClass(self.browsedpath, r['path'])
                # if browser path is current or current node
                # search for subfolders
                if r['path_class']:
                    r['sub_folders'] = self.finderNavBrowsingResults(querypath=r['path'])

            results.append(r)

        return results


    def finderResults(self):
        """Return results to select
        """
        cat = self.data['catalog']
        scope = self.data['scope']
        if IATTopic.providedBy(scope):
            supQuery = self.finderQuery()
            if supQuery.has_key('path'):
                del supQuery['path']
            brains = finderTopicsQueryCatalog(scope, cat, **supQuery)
        else:
            query = self.finderQuery()
            brains = cat(**query)
        results = []
        for b in brains:
            title_or_id = b.pretty_title_or_id()
            r = {
                'uid': b.UID,
                'url': b.getURL(),
                'path': b.getPath(),
                'title': title_or_id,
                'jstitle': title_or_id.replace("\x27", "\x5C\x27"),
                'description':b.Description,
                'state_class': 'state-%s' % b.review_state,
                'is_folderish': b.is_folderish or False,
                'size': b.getObjSize,
                'type': b.portal_type,
                'blacklisted': False,
                'created': b.created,
                'actions_menu': {}
                }
            if r['type'] in self.imagestypes:
                o = b.getObject()
                imageInfos = self.getImageInfos(o)
                orientation = imageInfos[0]
                width = imageInfos[1]
                height = imageInfos[2]
                if width and height:
                    # FIXME: This should go in config.py
                    min, max = 70, 100
                    if orientation == 'portrait':
                        ratio = float(width)/float(height)
                        if height > max:
                            width = int(ratio *max)
                            height = max
                        if width > min:
                            width = min
                            height = int(min/ratio)
                    else:
                        ratio = float(height)/float(width)
                        if width > max:
                            height = int(ratio *max)
                            width = max
                        if height > min:
                            height = min
                            width = int(min/ratio)
                    thumb_sizes = self.getThumbSizes()
                    # define thumb icon and preview urls for display
                    thumb = icon = '%s/image' % r['url']
                    preview = '%s/image?isImage=1' % r['url']
                    for ts in thumb_sizes:
                        if ts[1] >= width and ts[2] >= height:
                            thumb = '%s/@@images/image/%s' % (r['url'], ts[0])
                            break
                    for ts in thumb_sizes:
                        if ts[1] >= 16 and ts[2] >= 16:
                            icon = '%s/@@images/image/%s' % (r['url'], ts[0])
                            break
                    for ts in thumb_sizes:
                        if ts[1] >= 400 and ts[2] >= 400:
                            preview = '%s/@@images/image/%s?isImage=1' % (r['url'], ts[0])
                            break
                    # images sizes actions menu
                    thumb_sizes.extend([('full',width ,height ,_('Full size'), '/image')])
                    if self.allowimagesizeselection:
                        r['actions_menu']['choose_image_size'] = {
                            'label': _(u'Choose image size'),
                            'actions': thumb_sizes
                            }
                    r.update({
                        'is_image': True,
                        'preview_url': preview,
                        'url': '%s/image' % r['url'],
                        'container_class': 'imageContainer',
                        'style': 'width: %ipx; height: %ipx' % (width, height)
                        })
                else:
                    orientation = 'small'
                    thumb = icon = None
                    r.update({
                        'iconclass': ('contenttype-%s divicon' %
                                      b.portal_type.lower().replace(' ','-')),
                        'is_image': False,
                        'container_class': 'fileContainer',
                        'style': ''
                        })
            else:
                # Not an image type
                orientation = 'small'
                r['style'] = ''
                if b.portal_type in self.filestypes:
                    o = b.getObject()
                    icon_base = o.getIcon()
                    if icon_base:
                        r['style'] = 'background-image: url(./%s)' % icon_base
                r['iconclass'] = 'contenttype-%s divicon' % b.portal_type.lower().replace(' ','-')
                thumb = icon = None
                r['is_image'] = False
                r['container_class'] = 'fileContainer'
            if self.typeview == 'image':
                r['orientation_class'] = orientation
                r['thumb'] = thumb
            else:
                r['orientation_class'] = '%s_icon' % orientation
                r['thumb'] = icon

            if r['size']:
                r['real_size'] = float(r['size'].split(' ')[0])
            else:
                r['real_size'] = 0

            results.append(r)

        return results


    def getThumbSizes(self):
        """Return an ordered list of thumb sizes taken from portal properties
        imaging properties when exists list of tuples [(label, width, height,
        thumb_label, thumb_extension), ...]
        FIXME: This is too much associated with standard ATImage. We should proceed
        with views/adapters
        """
        context = aq_inner(self.context)
        pprops = getToolByName(context, 'portal_properties')
        if hasattr(pprops, 'imaging_properties'):
            imaging_properties = pprops.imaging_properties
            thumb_sizes_props = imaging_properties.getProperty('allowed_sizes')
            thumb_sizes = []
            for prop in thumb_sizes_props:
                propInfo = prop.split(' ')
                thumb_name = propInfo[0]
                thumb_width = int(propInfo[1].split(':')[0])
                thumb_height = int(propInfo[1].split(':')[1])
                thumb_label = "%s : %ipx*%ipx" % (_(thumb_name.capitalize()), thumb_width,
                                                  thumb_height)
                thumb_extension = "/@@images/image/%s" % thumb_name
                thumb_sizes.append((thumb_name, thumb_width, thumb_height, thumb_label,
                                    thumb_extension))
            thumb_sizes.sort(key=lambda ts: ts[1])
            return thumb_sizes

        return [
            ('listing', 16, 16, '%s : 16px*16px' % _('Listing'), '/@@images/image/listing'),
            ('icon', 32, 32, '%s : 32px*32px' % _('Icon'), '/@@images/image/icon'),
            ('tile', 64, 64, '%s : 64px*64px' % _('Tile'), '/@@images/image/tile'),
            ('thumb', 128, 128, '%s : 128px*128px' % _('Thumb'), '/@@images/image/thumb'),
            ('mini', 200, 200, '%s : 200px*200px' % _('Mini'), '/@@images/image/mini'),
            ('preview', 400, 400, '%s : 400px*400px' % _('Preview'), '/@@images/image/preview'),
            ('large', 768, 768, '%s : 768px*768px' % _('Large'), '/@@images/image/large')
            ]

    def getImageSize(self, image_obj):
        if HAS_PAC:
            if (
                IImage.providedBy(image_obj) or IImage.providedBy(image_obj)
            ):
                return image_obj.image.getImageSize()
        field = image_obj.getField('image')
        if field.type in ("blob", "file", "image"):
            return field.getSize(image_obj)
        elif field.type == "reference":
            return field.get(image_obj).getSize()
        else:
            raise ValueError("image field type unknown")


    def getImageInfos(self, image_obj):
        """Return orientation width and height
        # FIXME: This is too much associated to ATImage stuffs.
        We should proceed with adapters
        # FIXME: This should be a function, not a method
        """
        im_width, im_height = self.getImageSize(image_obj)
        if im_height >= im_width:
            orientation = 'portrait'
        else:
            orientation = 'landscape'
        return orientation, im_width, im_height


    def cleanRequest(self):
        """Remove some params in request and store some of them for next request
        FIXME: rename this 'cleanQuery' and make this a function that takes the
        request as parameter
        """
        request = self.request
        ignored = ('blacklist', 'addtoblacklist', 'removefromblacklist', 'searchsubmit',
                   'newsession', 'emptyblacklist', 'b_start', 'finder_sort_on',
                   'sort_order')
        dictRequest = {}
        for param, value in request.form.items():
            if (value is not None and
                (param not in ignored) and
                (param not in FORM_PARAMS)):
                dictRequest[param] = value

        return dictRequest


    def cleanQuery(self):
        """Make a query_string with clean Request
        """
        return make_query(self.cleanrequest)

