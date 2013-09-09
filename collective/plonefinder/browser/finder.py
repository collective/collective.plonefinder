
from ZTUtils import make_query
from zope.interface import implements

from Products.Five import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.interface import IATTopic

from collective.plonefinder.interfaces import IFinder
from interfaces import IFinderUploadCapable
from collective.plonefinder import siteMessageFactory as _


def _quotestring(s):
    return '"%s"' % s


def _quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, _quotestring(char))
    return s


def getPathClass(browsedpath, currentpath):
    """
    if currentpath == browsedpath return ' currentitem'
    if currentpath is parent of browsedpath return ' currentnode'
    else return ''
    """

    if currentpath == browsedpath:
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


def finderTopicsQueryCatalog(scope, catalog, **kw):
    """Redefine the queryCatlog method defined in AT Topics
       to allow a query override with kw args
       and to return 0 results when
       there are no criteria inside topic
       (other use cases are not interesting here)
    """

    query = scope.buildQuery()
    if query is None:
        return []
    else:
        # Allow parameters to override existing criterias
        for k, v in kw.items():
            query[k] = v
        return catalog(**query)

FORM_PARAMS = ('SearchableText',)


class Finder(BrowserView):
    """
    class for Plone Finder View
    """
    implements(IFinder)

    template = ViewPageTemplateFile('finder.pt')

    def __init__(self, context, request):
        super(Finder, self).__init__(context, request)
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        # dict to place persistent objects
        self.data = {}
        self.data['portal'] = portal
        self.data['root'] = None
        self.data['scope'] = None
        self.data['catalog'] = getToolByName(portal, 'portal_catalog')
        self.is_plone3 = self.isPlone3()
        self.portal_url = portal_url()
        self.portalpath = '/'.join(portal.getPhysicalPath())
        self.breadcrumbs = []
        # all these properties could be overloaded
        # in a Finder's inherited class
        self.findername = 'plone_finder'
        self.showbreadcrumbs = True
        self.scopetitle = ''
        self.scopetype = ''
        self.scopeiconclass = 'divicon'
        self.multiselect = True
        self.forcecloseoninsert = 0
        self.rootpath = ''
        self.browsedpath = ''
        self.parentpath = ''
        self.types = []
        self.typeview = 'file'
        self.typecss = 'list'
        self.browse = True
        self.sort_on = 'getObjPositionInParent'
        self.sort_order = ''
        self.sort_inverse = 'ascending'
        self.sort_request = False
        self.sort_withcatalog = True
        self.displaywithoutquery = True
        self.blacklist = []
        self.addtoblacklist = []
        self.removefromblacklist = []
        self.query = None
        self.imagestypes = ('Image', )
        self.filestypes = ('File')
        self.selectiontype = 'uid'
        self.allowimagesizeselection = True
        self.fieldid = 'demofield'
        self.fieldname = 'demofield'
        self.fieldtype = 'list'
        self.ispopup = True
        self.showblacklisted = True
        self.searchsubmit = False
        self.allowupload = False
        self.allowaddfolder = False
        self.typeupload = ''
        self.typefolder = ''
        # change this property
        # to define your own methods (overload selectItem as example)
        self.jsaddons = ''
        # change this property
        # to define your own css
        self.cssaddons = ''

    def __call__(self):

        context = aq_inner(self.context)
        request = aq_inner(self.request)
        session = request.get('SESSION', {})
        # use self.rootpath or rootpath in request or session
        # to change browser root
        self.rootpath = request.get('rootpath', self.rootpath)
        # use self.browse=False (or browse=False in request)
        # to disallow browsing globally
        self.browse = request.get('browse', self.browse)
        self.showbreadcrumbs = request.get('showbreadcrumbs',
                self.showbreadcrumbs)
        if not self.browse:
            self.showbreadcrumbs = False

        self.setScopeInfos(context, request, self.showbreadcrumbs)

        # use self.multiselect = False (or multiselect = False in request)
        # when multiselect is False window is closed on insert
        self.multiselect = request.get('multiselect', self.multiselect)
        # to force close on insert even in multiselect mode
        self.forcecloseoninsert = request.get('forcecloseoninsert',
                self.forcecloseoninsert)

        if not self.multiselect:
            self.forcecloseoninsert = 1

        # use self.types (or types in request) to specify portal_types
        # in catalog request
        self.types = request.get('types', self.types)

        # use self.typeupload (or typeupload in request)
        # to specify portal_type for upload
        self.typeupload = request.get('typeupload', self.typeupload)

        # use self.typefolder (or typefolder in request)
        # to specify portal_type used to create folder
        self.typefolder = request.get('typefolder', self.typefolder)

        # use self.typeview (or typeview in request)
        # to specify typeview ('file' or 'image' for now,
        # 'selection' in future)
        self.typeview = request.get('typeview', self.typeview)
        if self.typeview == 'image':
            self.typecss = 'float'

        if request.get('finder_sort_on'):
            self.sort_on = request.get('finder_sort_on')
            self.sort_order = request.get('sort_order', self.sort_order)
            # sort_order could be empty or reverse, or ascending
            if self.sort_order == 'reverse':
                self.sort_inverse = 'ascending'
            elif self.sort_order == 'ascending':
                self.sort_inverse = 'reverse'
            self.sort_request = True
            if self.sort_on not in self.data['catalog'].indexes():
                self.sort_withcatalog = False

        # use self.displaywithoutquery = False if necessary
        self.displaywithoutquery = request.get('displaywithoutquery',
                self.displaywithoutquery)

        # use self.blacklist (or blacklist in session or request)
        # to remove some uids from results
        rblacklist = request.get('blacklist', self.blacklist)
        sblacklist = session.get('blacklist', rblacklist)
        if (sblacklist and not rblacklist
                and not request.get('newsession', False)):
            self.blacklist = sblacklist
        else:
            self.blacklist = rblacklist

        # use self.addtoblacklist (or addtoblacklist in request)
        # to add elements in blacklist
        addtoblacklist = request.get('addtoblacklist', self.addtoblacklist)
        for k in addtoblacklist:
            if k not in self.blacklist:
                self.blacklist.append(k)

        # use self.removefromblacklist (or removefromblacklist in request)
        # to remove elements from blacklist
        removefromblacklist = request.get('removefromblacklist',
                self.removefromblacklist)
        for k in removefromblacklist:
            if k in self.blacklist:
                self.blacklist.remove(k)

        # put new blacklist in session
        if request.get('emptyblacklist', False):
            if session:
                session.set('blacklist', [])
        else:
            if session:
                session.set('blacklist', self.blacklist)

        # use self.query (or query in request) to overload entire query
        self.query = request.get('query', self.query)

        # imagestypes used to show or not thumbs in browser
        self.imagestypes = request.get('imagestypes', self.imagestypes)

        # filestypes used to show mime-type icons in browser
        self.filestypes = request.get('filestypes', self.filestypes)

        # use self.selectiontype or selectiontype in request
        # to overload selectiontype
        # could be 'uid' or 'url'
        self.selectiontype = request.get('selectiontype', self.selectiontype)

        # set it to False to disallow sizes menu
        self.allowimagesizeselection = request.get('allowimagesizeselection',
                self.allowimagesizeselection)

        # field id which will receive the selection
        self.fieldid = request.get('fieldid', self.fieldid)

        # TODO field name which will receive the selection
        self.fieldname = request.get('fieldname', self.fieldname)

        # TODO could be string
        self.fieldtype = request.get('fieldtype', self.fieldtype)

        # set self.ispopup = False or ispopup = False in request
        # for calling view in ajax
        self.ispopup = request.get('ispopup', self.ispopup)

        # set self.showblacklisted = True or showblacklisted in request
        # to show blacklist
        self.showblacklisted = request.get('showblacklisted',
                self.showblacklisted)

        # use self.self.searchsubmit = True (or searchsubmit = True in request)
        # to display search results
        self.searchsubmit = request.get('searchsubmit', self.searchsubmit)

        firstpassresults = self.finderResults()
        if self.sort_request and not self.sort_withcatalog:
            firstpassresults.sort(key=lambda k: k[self.sort_on])
            if self.sort_order == 'reverse':
                firstpassresults.reverse()

        # remove blacklisted uids or just set it as blacklisted if needed
        results = []

        if self.selectiontype == 'uid':
            for r in firstpassresults:
                if (r['uid'] not in self.blacklist
                        or self.typeview == 'selection'):
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

        self.allowupload = request.get('allowupload', self.allowupload)
        # upload disallowed if user do not have permission to
        # Add portal content on main window context
        if self.allowupload:
            tool = getToolByName(context, "portal_membership")
            if not(tool.checkPermission(
                'Add portal content', self.data['scope'])):
                self.allowupload = False
            if not IFinderUploadCapable.providedBy(self.data['scope']):
                self.allowupload = False

        self.allowaddfolder = request.get('allowaddfolder',
                self.allowaddfolder)
        # allowaddfolder disallowed if user do not have permission to
        # add portal content on context
        # disallowed also when context is not IFinderUploadCapable
        if self.allowaddfolder:
            tool = getToolByName(context, "portal_membership")
            if not(tool.checkPermission('Add portal content',
                self.data['scope'])):
                self.allowaddfolder = False
            if not IFinderUploadCapable.providedBy(self.data['scope']):
                self.allowaddfolder = False

        self.cleanrequest = self.cleanRequest()

        return self.template()

    def setScopeInfos(self, context, request, showbreadcrumbs):
        """
        set scope and all infos related to scope
        """
        browsedpath = request.get('browsedpath', self.browsedpath)
        portal = self.data['portal']
        # find browser root and rootpath if undefined
        if self.data['root'] is None:
            self.data['root'] = root = aq_inner(portal.restrictedTraverse(
                self.rootpath))
            if not self.rootpath:
                self.rootpath = '/'.join(root.getPhysicalPath())
        # find scope if undefined
        # by default scope = browsedpath or first parent folderish
        # or context if context is a folder
        scope = self.data['scope']
        if scope is None:
            if browsedpath:
                self.data['scope'] = scope = aq_inner(
                        portal.restrictedTraverse(browsedpath))
            else:
                folder = aq_inner(context)
                if not bool(getattr(
                            aq_base(folder), 'isPrincipiaFolderish', False)):
                    folder = aq_inner(folder.aq_parent)
                self.data['scope'] = scope = folder

        self.scopetitle = scope.pretty_title_or_id()
        self.scopetype = scopetype = scope.portal_type
        self.scopeiconclass = ('contenttype-%s divicon' %
                scopetype.lower().replace(' ', '-'))

        # set browsedpath and browsed_url
        self.browsedpath = '/'.join(scope.getPhysicalPath())
        self.browsed_url = scope.absolute_url()
        if scope is not self.data['root']:
            parentscope = aq_inner(scope.aq_parent)
            self.parentpath = '/'.join(parentscope.getPhysicalPath())

        # set breadcrumbs
        # TODO : use self.data['catalog']
        portal_membership = getToolByName(context, "portal_membership")
        if showbreadcrumbs:
            crumbs = []
            item = scope
            itempath = self.browsedpath
            while itempath != self.rootpath:
                crumb = {}
                crumb['path'] = itempath
                crumb['title'] = item.title_or_id()
                crumb['show_link'] = portal_membership.checkPermission(
                        'View', item)
                crumbs.append(crumb)
                item = aq_inner(item.aq_parent)
                itempath = '/'.join(item.getPhysicalPath())
            crumbs.reverse()
            self.breadcrumbs = crumbs

    def finderQuery(self, topicQuery=None):
        """
        return query for results depending on some params
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
            path['query'] = self.browsedpath
            query['path'] = path
            sort_index = self.sort_on
            if self.sort_withcatalog:
                query['sort_on'] = sort_index
                query['sort_order'] = self.sort_order
            if self.types:
                query['portal_type'] = self.types

            if self.searchsubmit:
                # TODO : use a dynamic form
                # with different possible searchform fields
                q = request.get('SearchableText', '')
                if q:
                    for char in '?-+*':
                        q = q.replace(char, ' ')
                    r = q.split()
                    r = " AND ".join(r)
                    searchterms = _quote_bad_chars(r) + '*'

                    query['SearchableText'] = searchterms

            return query

    def finderNavBrowsingResults(self, querypath=''):
        """
        method used to get left navigation subtree results
        """
        if not querypath:
            querypath = self.rootpath
        return self.finderBrowsingResults(querypath=querypath, isnav=True)

    def finderBrowsingQuery(self, querypath=None):
        """
        return query for folderishs to browse
        """
        if self.browse:
            query = {}
            path = {}
            path['depth'] = 1
            if querypath:
                path['query'] = querypath
            else:
                path['query'] = self.browsedpath
            query['path'] = path
            query['is_folderish'] = True
            query['sort_on'] = 'getObjPositionInParent'
            return query

    def finderBrowsingResults(self, querypath=None, isnav=False):
        """
        return results to browse
        method used for finder left navigation
        and navigation inside main window
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
            r['iconclass'] = ('contenttype-%s divicon' %
                    b.portal_type.lower().replace(' ', '-'))
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
                    r['sub_folders'] = self.finderNavBrowsingResults(
                            querypath=r['path'])

            results.append(r)

        return results

    def finderResults(self):
        """
        return results to select
        """
        cat = self.data['catalog']
        scope = self.data['scope']
        if IATTopic.providedBy(scope):
            supQuery = self.finderQuery()
            if 'path' in supQuery:
                del supQuery['path']
            brains = finderTopicsQueryCatalog(scope, cat, **supQuery)
        else:
            query = self.finderQuery()
            brains = cat(**query)
        results = []
        for b in brains:
            r = {}
            r['uid'] = b.UID
            r['url'] = b.getURL()
            r['path'] = b.getPath()
            r['title'] = b.pretty_title_or_id()
            r['jstitle'] = r['title'].replace("\x27", "\x5C\x27")
            r['description'] = b.Description
            r['state_class'] = 'state-%s' % b.review_state
            r['is_folderish'] = b.is_folderish or False
            r['size'] = b.getObjSize
            r['type'] = b.portal_type
            r['blacklisted'] = False
            r['created'] = b.created
            r['actions_menu'] = {}
            if r['type'] in self.imagestypes:
                o = b.getObject()
                imageInfos = self.getImageInfos(o)
                orientation = imageInfos[0]
                width = imageInfos[1]
                height = imageInfos[2]
                if width and height:
                    min, max = 70, 100
                    if orientation == 'portrait':
                        ratio = float(width) / float(height)
                        if height > max:
                            width = int(ratio * max)
                            height = max
                        if width > min:
                            width = min
                            height = int(min / ratio)
                    else:
                        ratio = float(height) / float(width)
                        if width > max:
                            height = int(ratio * max)
                            width = max
                        if height > min:
                            height = min
                            width = int(min / ratio)
                    thumb_sizes = self.getThumbSizes()
                    # define thumb icon and preview urls for display
                    thumb = icon = '%s/image' % r['url']
                    preview = '%s/image?isImage=1' % r['url']
                    for ts in thumb_sizes:
                        if ts[1] >= width and ts[2] >= height:
                            thumb = '%s/image_%s' % (r['url'], ts[0])
                            break
                    for ts in thumb_sizes:
                        if ts[1] >= 16 and ts[2] >= 16:
                            icon = '%s/image_%s' % (r['url'], ts[0])
                            break
                    for ts in thumb_sizes:
                        if ts[1] >= 400 and ts[2] >= 400:
                            preview = ('%s/image_%s?isImage=1' %
                                    (r['url'], ts[0]))
                            break
                    # images sizes actions menu
                    thumb_sizes.extend([('full', width, height, _('Full size'),
                        '/image')])
                    if self.allowimagesizeselection:
                        r['actions_menu']['choose_image_size'] = {
                                'label': _(u'Choose image size'),
                                'actions': thumb_sizes}
                    r['is_image'] = True
                    r['preview_url'] = preview
                    r['url'] = '%s/image' % r['url']
                    r['container_class'] = 'imageContainer'
                    r['style'] = 'width: %ipx; height: %ipx' % (width, height)
                else:
                    orientation = 'small'
                    thumb = icon = None
                    r['iconclass'] = ('contenttype-%s divicon' %
                            b.portal_type.lower().replace(' ', '-'))
                    r['is_image'] = False
                    r['container_class'] = 'fileContainer'
                    r['style'] = ''
            else:
                orientation = 'small'
                r['style'] = ''
                if b.portal_type in self.filestypes:
                    o = b.getObject()
                    icon_base = o.getIcon()
                    if icon_base:
                        r['style'] = 'background-image: url(./%s)' % icon_base
                r['iconclass'] = ('contenttype-%s divicon'
                        % b.portal_type.lower().replace(' ', '-'))
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
        """
        return an ordered list of thumb sizes
        taken from portal properties imaging properties
        when exists
        list of tuples [(label, width, height, thumb_label, thumb_extension)]
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
                thumb_label = "%s : %ipx*%ipx" % (
                        _(thumb_name.capitalize()), thumb_width, thumb_height)
                thumb_extension = "/image_%s" % thumb_name
                thumb_sizes.append((thumb_name, thumb_width, thumb_height,
                    thumb_label, thumb_extension))
            thumb_sizes.sort(key=lambda ts: ts[1])
            return thumb_sizes

        return [('listing', 16, 16, '%s : 16px*16px' % _('Listing'),
                    '/image_listing'),
                ('icon', 32, 32, '%s : 32px*32px' % _('Icon'), '/image_icon'),
                ('tile', 64, 64, '%s : 64px*64px' % _('Tile'), '/image_tile'),
                ('thumb', 128, 128, '%s : 128px*128px' % _('Thumb'),
                    '/image_thumb'),
                ('mini', 200, 200, '%s : 200px*200px' % _('Mini'),
                    '/image_mini'),
                ('preview', 400, 400, '%s : 400px*400px' % _('Preview'),
                    '/image_preview'),
                ('large', 768, 768, '%s : 768px*768px' % _('Large'),
                    '/image_large')]

    def getImageInfos(self, image_obj):
        """
        return orientation width and height
        """
        field = image_obj.getField('image')
        im_width, im_height = field.getSize(image_obj)
        if im_height >= im_width:
            orientation = 'portrait'
        else:
            orientation = 'landscape'
        return orientation, im_width, im_height

    def cleanRequest(self):
        """
        Remove some params in request
        and store some of them for next request
        """

        request = self.request
        ignored = ('blacklist', 'addtoblacklist', 'removefromblacklist',
                'searchsubmit', 'newsession', 'emptyblacklist', 'b_start',
                'finder_sort_on', 'sort_order')
        dictRequest = {}
        for param, value in request.form.items():
            if (value is not None and
                (param not in ignored) and
                (param not in FORM_PARAMS)):
                dictRequest[param] = value

        return dictRequest

    def cleanQuery(self):
        """
        make a query_string with clean Request
        """

        return make_query(self.cleanrequest)

    def isPlone3(self):
        """
        """
        context = aq_inner(self.context)
        mt = getToolByName(context, 'portal_migration')
        plone_version = mt.getInstanceVersion()
        if int(plone_version[0]) == 3:
            return True
        return False
