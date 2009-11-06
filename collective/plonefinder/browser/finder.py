from ZTUtils import make_query
from zope.component import getMultiAdapter
from zope.interface import implements
from Products.Five import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.ATContentTypes.interface import IImageContent

from collective.plonefinder.interfaces import IFinder


def _quotestring(s):
    return '"%s"' % s

def _quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, _quotestring(char))
    return s


FORM_PARAMS = ('SearchableText',)                                                


class Finder(BrowserView):
    """
    class for Plone Finder View
    """
    implements(IFinder)
    
    template = ViewPageTemplateFile('finder.pt')
    
    def __init__(self, context, request) :
        super(Finder, self).__init__(context, request)
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        self.portal_url = portal_url()
        self.portal = portal 
        self.portalpath = '/'.join(portal.getPhysicalPath())       
        self.breadcrumbs = []  
        # all these properties could be overloaded
        # in a Finder's inherited class
        self.findername = 'plone_finder'
        self.catalog =  getToolByName(self.portal, 'portal_catalog')
        self.showbreadcrumbs=True 
        self.scope = None
        self.multiselect = True
        self.browsedpath = ''
        self.parentpath = ''
        self.types = []
        self.typeview = 'file'
        self.typecss = 'list'
        self.browse = True
        self.displaywithoutquery = True
        self.blacklist = []
        self.addtoblacklist = [] 
        self.removefromblacklist = []
        self.query = None
        self.imagestypes = ['Image', 'News Item']
        self.selectiontype = 'uid'
        self.fieldid = 'demofield'
        self.fieldname = 'demofield'
        self.fieldtype = 'list'
        self.ispopup = True
        self.showblacklisted = False 
        self.searchsubmit = False  
        self.allowupload = False             
        
    
    def __call__(self):       
        
        context = aq_inner(self.context)
        request = aq_inner(self.request)                                       
        session = request.get('SESSION', None)  
        self.showbreadcrumbs =  request.get('showbreadcrumbs', self.showbreadcrumbs)
        self.setScopeInfos(context, request, self.showbreadcrumbs)                            
                    
        # use self.multiselect = False (or multiselect = False in request) to close window after selection
        self.multiselect = request.get('multiselect', self.multiselect)            
                 
        # use self.types (or types in request) to specify portal_types in catalog request
        self.types = request.get('types', self.types)    
        
        # use self.typeview (or typeview in request) to specify typeview ('file' or 'image' for now, 'selection' in future)
        self.typeview = request.get('typeview', self.typeview)    
        if self.typeview == 'image' :
            self.typecss = 'float'      
              
        # use self.browse=False (or browse=False in request) to disallow browsing
        self.browse = request.get('browse', self.browse)     
        
        # use self.displaywithoutquery = False if necessary         
        self.displaywithoutquery = request.get('displaywithoutquery', self.displaywithoutquery)  
              
        # use self.blacklist (or blacklist in session or request) to remove some uids from results
        rblacklist = request.get('blacklist', self.blacklist)
        sblacklist = session.get('blacklist', rblacklist)        
        if sblacklist and not rblacklist and not request.get('newsession', False) :
            self.blacklist = sblacklist
        else :
            self.blacklist = rblacklist
            
        # use self.addtoblacklist (or addtoblacklist in request) to add elements in blacklist 
        addtoblacklist = request.get('addtoblacklist', self.addtoblacklist)  
        for k in addtoblacklist :
            if k not in self.blacklist :
                self.blacklist.append(k)    
        
        # use self.removefromblacklist (or removefromblacklist in request) to remove elements from blacklist                       
        removefromblacklist = request.get('removefromblacklist', self.removefromblacklist)  
        for k in removefromblacklist :
            if k in self.blacklist :
                self.blacklist.remove(k)      
        
        # put new blacklist in session
        if request.get('emptyblacklist', False) :
            session.set('blacklist', [])
        else :
            session.set('blacklist', self.blacklist)
            
        # use self.query (or query in request) to overload entire query
        self.query = request.get('query', self.query)         
        
        # TODO Images types in portal properties
        self.imagestypes = ['Image', 'News Item']
        
        # use self.selectiontype or selectiontype in request to overload selectiontype
        # could be 'uid' or 'url'
        self.selectiontype = request.get('selectiontype', self.selectiontype) 
        
        # TODO field id which will receive the selection
        self.fieldid = 'demofield' 
        
        # TODO field name which will receive the selection   
        self.fieldname = 'demofield'   
        
        # TODO could be string
        self.fieldtype = request.get('fieldtype', self.fieldtype)        
        
        # set self.ispopup = False or ispopup = False in request for calling view in ajax
        self.ispopup = request.get('ispopup', self.ispopup)         
        
        # set self.showblacklisted = True or showblacklisted in request to show blacklist
        self.showblacklisted = request.get('showblacklisted', self.showblacklisted)          
        
        # use self.self.searchsubmit = True (or searchsubmit = True  in request) to display search results
        self.searchsubmit = request.get('searchsubmit', self.searchsubmit)          
                          
        firstpassresults = self.finderResults()        
        resultids = [r['uid'] for r in firstpassresults]   
        
        # remove blacklisted uids or just set it as blacklisted if needed
        results = []

        if self.selectiontype == 'uid' :
            for r in firstpassresults :
                if r['uid'] not in self.blacklist or self.typeview=='selection' :
                    results.append(r)
                elif  self.showblacklisted :
                    r['blacklisted'] = True
                    results.append(r)
            firstpassresults = results                   
        
        # if we can browse, we must remove folders from results
        # and we must set these folders as linkables
        if self.browse :
            results = []
            firstpassfolders = self.finderBrowsingResults()
            folderids = [f['uid'] for f in firstpassfolders]
            for r in firstpassresults :
                if r['uid'] not in folderids :
                    results.append(r)
            self.results = results    
            folders = []
            for f in firstpassfolders :
                if f['uid'] in resultids :    
                    f['islinkable'] = True
                else :     
                    f['islinkable'] = False
                folders.append(f)
            self.folders = folders        
        else :
            self.results = firstpassresults  
            self.folders = [] 
                   
        self.cleanrequest = self.cleanRequest()          
        
        # upload disallowed if user do not have permission to 
        # modify portal content on context        
        if self.allowupload :
            tool = getToolByName(context, "portal_membership")
            if not(tool.checkPermission('Modify portal content', context)) :
                self.allowupload = False                
        
        return self.template()             

    
    def setScopeInfos(self, context, request, showbreadcrumbs):
        """
        set scope and all infos related to scope
        """
        browsedpath = request.get('browsedpath', self.browsedpath)
        # find scope if undefined
        # by default scope = browsedpath or first parent folderish or context if context is a folder        
        scope = self.scope
        if scope is None  : 
            if browsedpath :
                scope = self.scope = aq_inner(self.portal.restrictedTraverse(browsedpath))   
            else :
                folder = context
                while not IPloneSiteRoot.providedBy(folder)  : 
                    if bool(getattr(aq_base(folder), 'isPrincipiaFolderish', False)) :
                        break
                    folder = aq_inner(folder.aq_parent)    
                scope = self.scope = folder                
        
        # set browsedpath and browsed_url
        if not IPloneSiteRoot.providedBy(scope) : 
            self.browsedpath = '/'.join(scope.getPhysicalPath())        
            self.browsed_url = scope.absolute_url()
            parentscope = aq_inner(scope.aq_parent)
            if not IPloneSiteRoot.providedBy(parentscope) :
                self.parentpath = '/'.join(parentscope.getPhysicalPath()) 
            else :
                self.parentpath =  self.portalpath   
        else :
            self.browsedpath = self.portalpath
            self.browsed_url = self.portal_url     
        
        # set breadcrumbs    
        # TODO : use self.catalog                     
        if showbreadcrumbs :
            crumbs = []
            item = scope
            while not IPloneSiteRoot.providedBy(item) :
                 crumb = {}
                 crumb['path'] = '/'.join(item.getPhysicalPath())
                 crumb['title'] = item.title_or_id()
                 crumbs.append(crumb)
                 item = aq_inner(item.aq_parent)
            crumbs.reverse()
            self.breadcrumbs = crumbs                   
        
                          
    def finderQuery(self) :
        """
        return query for results depending on some params
        """
        
        request = self.request
        if self.query :
            return self.query
        elif self.typeview == 'selection':
            return {'uid' : self.blacklist}            
        elif self.displaywithoutquery or self.searchsubmit :
            query = {}        
            path = {}
            if not self.searchsubmit :
                path['depth'] = 1
            path['query'] =  self.browsedpath
            query['path'] = path
            query['sort_on'] = 'getObjPositionInParent'
            if self.types :
                query['portal_type'] = self.types            
                                    
            if self.searchsubmit :
                # TODO : use a dynamic form with different possible searchform fields   
                q = request.get('SearchableText', '')    
                if q :            
                    for char in '?-+*':
                        q = q.replace(char, ' ')
                    r=q.split()
                    r = " AND ".join(r)
                    searchterms = _quote_bad_chars(r)+'*'                
                    
                    query['SearchableText'] = searchterms
            
            #query = {'path': {'query': '/cktest', 'depth': 2}, 'sort_on': 'getObjPositionInParent'}
            return query            
            
    def finderBrowsingQuery(self) :
        """
        return query for folderishs to browse
        """
        

        if self.browse :
            query = {}        
            path = {}
            path['depth'] = 1
            path['query'] =  self.browsedpath
            query['path'] = path
            query['is_folderish'] = True
            query['sort_on'] = 'getObjPositionInParent'
            return query
            
                       
    
    def finderBrowsingResults (self) :
        """
        return results to browse
        """ 
        cat = self.catalog
        query = self.finderBrowsingQuery()
        brains = cat(**query)           
        results = []
        for b in brains :
            r = {}
            r['uid'] = b.UID
            r['url'] = b.getURL()
            r['title'] = b.pretty_title_or_id()
            r['description'] = b.Description                 
            r['thumb'] = '%s/%s' %(self.portal_url, b.getIcon)
            r['type'] = b.portal_type
            r['path'] = b.getPath
            r['state_class'] = 'state-%s' %b.review_state 

            results.append(r)
        
        return results        

    
    def finderResults (self) :
        """
        return results to select
        """           
        context = aq_inner(self.context)                         
        cat = self.catalog
        query = self.finderQuery()        
        brains = cat(**query)    
        results = []
        for b in brains :
            r = {}
            r['uid'] = b.UID
            r['url'] = b.getURL()
            r['path'] = b.getPath
            r['title'] = b.pretty_title_or_id()
            r['description'] = b.Description
            r['state_class'] = 'state-%s' %b.review_state 
            r['is_folderish'] = b.is_folderish or False
            r['size'] = b.getObjSize
            r['type'] = b.portal_type
            r['blacklisted'] = False
            if r['type'] in self.imagestypes :
                o = b.getObject()
                orientation = self.getOrientationFor(o)
                thumb = '%s/image_thumb' %r['url']
                icon = '%s/image_listing' %r['url']
                r['is_image'] = True
                r['preview_url'] = '%s/image?isImage=1' %r['url']
                r['url'] = '%s/image' %r['url']
                r['container_class'] = 'imageContainer'
            else :    
                orientation = 'small'
                thumb = icon = b.getIcon
                r['is_image'] = False
                r['container_class'] = 'fileContainer'
            if self.typeview == 'image' :
                r['orientation_class'] =  orientation
                r['thumb'] = thumb
            else :
                r['orientation_class'] =  '%s_icon' %orientation       
                r['thumb'] = icon

            results.append(r)
        
        return results    
                                 


    def getOrientationFor(self, image_obj):        

        field = image_obj.getField('image')
        im_width, im_height = field.getSize(image_obj)

        if im_height >= im_width:
            return 'portrait'

        return 'landscape'              
        
    def cleanRequest(self):
        """
        Remove some params in request
        and store some of them for next request
        """

        request = self.request                        
        ignored = ('blacklist', 'addtoblacklist', 'removefromblacklist', 'searchsubmit', 'newsession', 'emptyblacklist', 'b_start')
        dictRequest = {}
        for param, value in request.form.items():
            if (value and
                (param not in ignored) and
                (param not in FORM_PARAMS)):
                dictRequest[param] = value
        
        return dictRequest        
                
    def cleanQuery(self) :         
        """
        make a query_string with clean Request
        """
        
        cleanquery = make_query(self.cleanrequest).replace('%20', '+')
        return cleanquery               
        
class FinderUploadView(BrowserView):
    """ The Finder Upload View
    """

    template = ViewPageTemplateFile("finder_upload.pt")

    def __call__(self):
        return self.template()

FINDER_UPLOAD_JS = """
    function all_complete(event, data) {
        //alert(data.filesUploaded + " Files Uploaded!");
        //alert(data.errors + " Errors");
        //alert(data.speed + " Avg. Speed");
        location.reload();
    };
    jq(document).ready(function() {
        jq('#uploader').fileUpload({
            'uploader'      : '%(portal_url)s/++resource++uploader.swf',
            'script'        : '%(context_url)s/@@upload_file',
            'cancelImg'     : '++resource++cancel.png',
            'folder'        : '%(physical_path)s',
            'scriptData'    : {'__ac': '%(__ac_cookie)s'},
            'onAllComplete' : Browser.onUploadComplete,
            'auto'          : %(ul_auto_upload)s,
            'multi'         : %(ul_allow_multi)s,
            'simUploadLimit': '%(ul_sim_upload_limit)s',
            'sizeLimit'     : '%(ul_size_limit)s',
            'fileDesc'      : '%(ul_file_description)s',
            'fileExt'       : '%(ul_file_extensions)s',
            'buttonText'    : '%(ul_button_text)s',
            'buttonImg'     : '%(ul_button_image)s',
            'scriptAccess'  : '%(ul_script_access)s',
            'hideButton'    : %(ul_hide_button)s
        });
    });
"""

        
class FinderUploadInit(BrowserView):
    """ Initialize uploadify js
    """

    def __init__(self, context, request):
        super(FinderUploadInit, self).__init__(context, request)
        self.context = aq_inner(context)

    def upload_settings(self):
        sp = getToolByName(self.context, "portal_properties").site_properties
        portal_url = getToolByName(self.context, 'portal_url')

        settings = dict(
            __ac_cookie         = self.request.cookies.get('__ac', ''),
            portal_url          = portal_url(),
            context_url         = self.context.absolute_url(),
            physical_path       = "/".join(self.context.getPhysicalPath()),
            ul_auto_upload      = sp.getProperty('ul_auto_upload', 'true'),
            ul_allow_multi      = sp.getProperty('ul_allow_multi', 'true'),
            ul_sim_upload_limit = sp.getProperty('ul_sim_upload_limit', 4),
            ul_size_limit       = sp.getProperty('ul_size_limit', ''),
            ul_file_description = sp.getProperty('ul_file_description', ''),
            ul_file_extensions  = sp.getProperty('ul_file_extensions', '*.*;'),
            ul_button_text      = sp.getProperty('ul_button_text', 'BROWSE'),
            ul_button_image     = sp.getProperty('ul_button_image', ''),
            ul_hide_button      = sp.getProperty('ul_hide_button', 'false'),
            ul_script_access    = sp.getProperty('ul_script_access', 'sameDomain'),
        )
        return settings

    def __call__(self):
        settings = self.upload_settings()
        return FINDER_UPLOAD_JS % settings        