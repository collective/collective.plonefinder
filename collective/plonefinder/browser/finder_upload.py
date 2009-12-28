# code taken from collective.uploadify
# for the base of the logic
# with some ameliorations
# use the ticket.py from PloneFlashUpload
# to avoid authentification problems with flash upload form

import mimetypes

from Acquisition import aq_inner, aq_parent
from AccessControl import SecurityManagement

from zope.security.interfaces import Unauthorized
from zope.filerepresentation.interfaces import IFileFactory

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile 

import ticket as ticketmod
from collective.plonefinder import logger


def encode(s):
    """ encode string
    """

    return "d".join(map(str, map(ord, s)))
    
    
def find_user(context, userid):
    """Walk up all of the possible acl_users to find the user with the
    given userid.
    """

    track = set()

    acl_users = aq_inner(getToolByName(context, 'acl_users'))
    path = '/'.join(acl_users.getPhysicalPath())
    logger.debug('Visited acl_users "%s"' % path)
    track.add(path)

    user = acl_users.getUserById(userid)
    while user is None and acl_users is not None:
        context = aq_parent(aq_parent(aq_inner(acl_users)))
        acl_users = aq_inner(getToolByName(context, 'acl_users'))
        if acl_users is not None:
            path = '/'.join(acl_users.getPhysicalPath())
            logger.debug('Visited acl_users "%s"' % path)
            if path in track:
                logger.warn('Tried searching an already visited acl_users, '
                            '"%s".  All visited are: %r' % (path, list(track)))
                break
            track.add(path)
            user = acl_users.getUserById(userid)

    if user is not None:
        user = user.__of__(acl_users)

    return user
    


class FinderUploadView(BrowserView):
    """ The Finder Upload View
    """

    template = ViewPageTemplateFile("finder_upload.pt")

    def __call__(self):
        return self.template()

FINDER_UPLOAD_JS = """
    jQuery(document).ready(function() {
        jQuery('#uploader').uploadify({
            'uploader'      : '%(portal_url)s/++resource++plonefinder_static/uploader.swf',
            'script'        : '%(context_url)s/@@finder_upload_file',
            'cancelImg'     : '%(portal_url)s/++resource++plonefinder_static/cancel.png',
            'folder'        : '%(physical_path)s',
            'scriptData'    : {'ticket': '%(ticket)s'},
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
        context = aq_inner(self.context)
        sp = getToolByName(context, "portal_properties").site_properties
        portal_url = getToolByName(context, 'portal_url')()        
        ticket = context.restrictedTraverse('@@ticket')()
        settings = dict(
            ticket              = ticket,
            portal_url          = portal_url,
            context_url         = context.absolute_url(),
            physical_path       = "/".join(context.getPhysicalPath()),
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
        
        
class FinderUploadFile(BrowserView):
    """ Upload a file
    """
                            
    def finder_upload_file(self) :
        
        context = aq_inner(self.context)
        request = self.request
        session = request.get('SESSION', None)
        
        ticket = self.request.form.get('ticket',None)
        if ticket is None:
            # try to get ticket from QueryString in cas of GET method
            qs = self.request.get('QUERY_STRING','ticket=')
            ticket = qs.split('=')[-1] or None

        logger.debug('Ticket being used is "%s"' % str(ticket))        
        
        logger.info('Ticket being used is "%s"' % str(ticket))   

        if ticket is None:
            raise Unauthorized('No ticket specified')             
        
        url = context.absolute_url()
        username = ticketmod.ticketOwner(url, ticket)
        if username is None:
            logger.warn('Ticket "%s" was invalidated, cannot be used '
                        'any more.' % str(ticket))
            raise Unauthorized('Ticket is not valid')

        old_sm = SecurityManagement.getSecurityManager()
        user = find_user(context, username)
        SecurityManagement.newSecurityManager(self.request, user)
        logger.debug('Switched to user "%s"' % username)
        
        # we must do it only when multiupload is finished
        # ticketmod.invalidateTicket(url,ticket)        
        
        file_name = request.form.get("Filename", "")
        file_data = request.form.get("Filedata", None)
        content_type = mimetypes.guess_type(file_name)[0]
        portal_type = session.get('typeupload', request.get('typeupload', ''))
        
        if not portal_type :
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(file_name.lower(), '', '') or 'File'
        
        if file_data:
            factory = IFileFactory(context)
            logger.info("uploading file: filename=%s, content_type=%s, portal_type=%s" % \
                    (file_name, content_type, portal_type))                             
            
            f = factory(file_name, content_type, file_data, portal_type)
            logger.info("file url: %s" % f.absolute_url())
        
            SecurityManagement.setSecurityManager(old_sm)   

            return f.absolute_url()        
    
    
    def __call__(self):
        """
        """        
        return self.finder_upload_file()  
        
                             