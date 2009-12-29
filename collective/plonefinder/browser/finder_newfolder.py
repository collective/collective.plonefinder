# code taken from collective.uploadify
# for the base of the logic
# with some ameliorations
# use the ticket.py from PloneFlashUpload
# to avoid authentification problems with flash upload form

import mimetypes

from Acquisition import aq_inner

from zope.filerepresentation.interfaces import IDirectoryFactory

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile 
from collective.plonefinder import logger
    

class FinderNewFolderView(BrowserView):
    """ Create folder form
    """ 
    
    template = ViewPageTemplateFile('finder_newfolder.pt')
    
    def __call__(self):
        """
        """        
        return self.template()             
        
class FinderNewFolder(BrowserView):
    """ Create a folder
    """
    def __call__(self):
        """
        """        
        return self.create_folder()  
                        
    
    def create_folder(self) :
        """
        create folder
        """
        context = aq_inner(self.context)
        request = self.request
        session = request.get('SESSION', None)
        
        portal_type = session.get('typefolder', request.get('typefolder', 'Folder'))     
       
        title = request.get('folder-title', '')
        description = request.get('folder-description', '')

        factory = IDirectoryFactory(context)
        logger.info("creating folder: title=%s, description=%s, portal_type=%s" % \
                   (title, description, portal_type))                             
        
        f = factory(title, description, portal_type)
        logger.info("folder url: %s" % f.absolute_url())
    

        return f.absolute_url()        
    
    
    def __call__(self):
        """
        """        
        return self.create_folder()  
        
                             