from zope.interface import implements
from Products.Five import BrowserView
from Acquisition import aq_base, aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.ATContentTypes.interface import IImageContent

from collective.plonefinder.interfaces import IFinder


def _quotestring(s):
    return '"%s"' % s

def _quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, _quotestring(char))
    return s

                                                


class Finder(BrowserView):
    """
    class for Plone Finder View
    """
    implements(IFinder)
    
    def __init__(self, context, request, **kwargs):
        BrowserView.__init__(self, context, request)
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        self.portal_url = portal_url()
        self.portal = portal 
        self.portalpath = '/'.join(portal.getPhysicalPath())        
        browsedpath = request.get('browsedpath', '')                
        
        session = request.get('SESSION', None)  
        
        # use self.catalog to change catalog
        if kwargs.has_key('catalog') : 
            self.catalog = kwargs['catalog']
        else :
            self.catalog = getToolByName(portal, 'portal_catalog')       
        # use self.scope to change scope (by default = first parent folderish)        
        if kwargs.has_key('scope') : 
            self.scope = kwargs['scope']    
        elif browsedpath :
            self.scope = portal.restrictedTraverse(browsedpath)   
        else :
            folder = aq_inner(context)
            while not (folder is portal) : 
                if bool(getattr(aq_base(folder), 'isPrincipiaFolderish', False)) :
                    break
                folder = folder.aq_parent    
            self.scope = folder
        self.browsedpath = ''
        self.parentpath = ''
        if not (self.scope is portal):
              self.browsedpath = '/'.join(aq_inner(self.scope).getPhysicalPath())  
              self.parentpath = '/'.join(aq_inner(self.scope).aq_parent.getPhysicalPath())       
        self.browsed_url = self.scope.absolute_url()
                    
        # use self.multiselect = False (or multiselect = False in request) to close window after selection
        if kwargs.has_key('multiselect') : 
            multiselect = kwargs['multiselect']
        else :
            multiselect = True
        self.multiselect = request.get('multiselect', multiselect)           
        # use self.types (or types in request) to specify portal_types in catalog request
        if kwargs.has_key('types') : 
            types = kwargs['types']
        else :
            types = []
        self.types = request.get('types', types)    
        # use self.typeview (or typeview in request) to specify typeview ('standard' or 'image' for now)
        if kwargs.has_key('typeview') : 
            typeview = kwargs['typeview']
        else :
            typeview = 'file'
        self.typeview = request.get('typeview', typeview)    
        if self.typeview == 'image' :
            self.typecss = 'float'
        else :
            self.typecss = 'list'                
        # use self.browse=False (or browse=False in request) to disallow browsing
        if kwargs.has_key('browse') : 
            browse = kwargs['browse']
        else :
            browse = True
        self.browse = request.get('browse', browse)     
        # use self.displaywithoutquery = False if necessary         
        if kwargs.has_key('displaywithoutquery') : 
            displaywithoutquery = kwargs['displaywithoutquery']
        else :
            displaywithoutquery = True
        self.displaywithoutquery = request.get('displaywithoutquery', displaywithoutquery)         
        # use self.blacklist (or blacklist in session or request) to remove some uids from results
        if kwargs.has_key('blacklist') : 
            blacklist = kwargs['blacklist']
        else :
            blacklist = []
        rblacklist = request.get('blacklist', blacklist)
        sblacklist = session.get('blacklist', blacklist)        
        if sblacklist and not rblacklist :
            self.blacklist = sblacklist
        else :    
            self.blacklist = rblacklist  
        # add or remove in blacklist
        if kwargs.has_key('addtoblacklist') : 
            addtoblacklist = kwargs['addtoblacklist']
        else :
            addtoblacklist = []   
        addtoblacklist = request.get('addtoblacklist', addtoblacklist)  
        for k in addtoblacklist :
            if k not in self.blacklist :
                self.blacklist.append(k)        
        if kwargs.has_key('removefromblacklist') : 
            removefromblacklist = kwargs['removefromblacklist']
        else :
            removefromblacklist = []              
        removefromblacklist = request.get('removefromblacklist', removefromblacklist)  
        for k in removefromblacklist :
            if k in self.blacklist :
                self.blacklist.remove(k)      
        # put new blacklist in session
        session.set('blacklist', self.blacklist)
        # use self.query (or query in request) to overload entire query
        if kwargs.has_key('query') : 
            query = kwargs['query']
        else :
            query = None
        self.query = request.get('query', query)         
        # TODO Images types in portal properties
        self.imagestypes = ['Image', 'News Item']
        
        # could be 'uid', 'url'
        if kwargs.has_key('selectiontype') : 
            self.selectiontype = kwargs['selectiontype']
        else :
            self.selectiontype = 'uid'
        
        # field id which will receive the selection
        self.fieldid = 'demofield' 
        
        # field name which will receive the selection   
        self.fieldname = 'demofield'   
        
        # could be string
        self.fieldtype = 'list'  
        
        self.showbreadcrumbs=True
        
        # set self.ispopup = False when calling view in ajax
        if kwargs.has_key('ispopup') : 
            ispopup = kwargs['ispopup']
        else :
            ispopup = True
        self.ispopup = request.get('ispopup', ispopup)         
        
        # set self.showblacklisted = True to show blacklist
        if kwargs.has_key('showblacklisted') : 
            showblacklisted = kwargs['showblacklisted']
        else :
            showblacklisted = False
        self.showblacklisted = request.get('showblacklisted', showblacklisted)          
                          
        firstpassresults = self.finderResults()        
        resultids = [r['uid'] for r in firstpassresults]   
        
        # remove blacklisted uids or just set it as blacklisted if needed      
        results = []        
        if self.selectiontype == 'uid' :
            for r in firstpassresults :
                if r['uid'] not in self.blacklist or self.showblacklisted :
                    if self.showblacklisted :
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
                   

      
        
    def finderBreadCrumbs(self) :
        """
        return breadcrumbs for plone finder
        """    
        
        scope = self.scope
        request =self.request
        breadcrumbs = utils.createBreadCrumbs(scope, self.request) 
        serverurl = request.get('SERVER_URL', '')
        newcrumbs = []
        for crumb in breadcrumbs :
            crumb['path'] = crumb['absolute_url'].replace(serverurl, '')
            newcrumbs.append(crumb)
        return newcrumbs
        
                          
    def finderQuery(self) :
        """
        return query for results depending on some params
        """
        
        request = self.request
        if self.query :
            return self.query
        elif self.displaywithoutquery :
            scope = self.scope
            query = {}        
            path = {}
            path['depth'] = 1
            path['query'] =  '/'.join(scope.getPhysicalPath())
            query['path'] = path
            if self.types :
                query['portal_types'] = self.types
            
            
            # TODO : use a dynamic form with different possible searchform fields   
            q = request.get('SearchableText', '')    
            if q :            
                for char in '?-+*':
                    q = q.replace(char, ' ')
                r=q.split()
                r = " AND ".join(r)
                searchterms = _quote_bad_chars(r)+'*'                
                
                query['SearchableText'] = searchterms
            
            return query            
            
    def finderBrowsingQuery(self) :
        """
        return query for folderishs to browse
        """
        

        if self.browse :
            scope = self.scope
            query = {}        
            path = {}
            path['depth'] = 1
            path['query'] =  '/'.join(scope.getPhysicalPath())
            query['path'] = path
            query['is_folderish'] = True
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
        
