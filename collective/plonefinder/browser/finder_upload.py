# code taken from collective.uploadify
# for the base of the logic
# with many ameliorations

import mimetypes

from Acquisition import aq_inner, aq_parent
from AccessControl import SecurityManagement

from zope.security.interfaces import Unauthorized
from zope.filerepresentation.interfaces import IFileFactory

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile 
from Products.ATContentTypes.interfaces import IImageContent

import ticket as ticketmod
from collective.plonefinder import siteMessageFactory as _
from collective.plonefinder import logger


def encode(s):
    """ encode string
    """

    return "d".join(map(str, map(ord, s)))


def decode(s):
    """ decode string
    """

    return "".join(map(chr, map(int, s.split("d"))))
    
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

def _listTypesForInterface(context, interface):
    """
    List of portal types that have File interface
    @param context: context
    @param interface: Zope interface
    @return: ['Image', 'News Item']
    """
    archetype_tool = getToolByName(context, 'archetype_tool')
    all_types = archetype_tool.listRegisteredTypes(inProject=True)
    # zope3 Interface
    try :
        all_types = [tipe['portal_type'] for tipe in all_types
                      if interface.implementedBy(tipe['klass'])]
    # zope2 interface
    except :
        all_types = [tipe['portal_type'] for tipe in all_types
                      if interface.isImplementedByInstancesOf(tipe['klass'])]
    return dict.fromkeys(all_types).keys() 

class FinderUploadView(BrowserView):
    """ The Finder Upload View
    """

    template = ViewPageTemplateFile("finder_upload.pt")

    def __call__(self):
        context = aq_inner(self.context)
        return self.template()

FINDER_UPLOAD_JS = """
    addUploadifyFields = function(event, data ) {
        var labelfiletitle = jQuery('#uploadify_label_file_title').val();
        jQuery('.uploadifyQueueItem').each(function() {
            ID = jQuery(this).attr('id').replace('uploader','');
            if (!jQuery('.uploadField' ,this).length) {
              jQuery('.cancel' ,this).after('\
                  <div class="uploadField">\
                      <label>' + labelfiletitle + ' : </label> \
                      <input type="hidden" \
                             class="file_id_field" \
                             name="file_id" \
                             value ="'  + ID + '" /> \
                      <input type="text" \
                             class="file_title_field" \
                             id="title_' + ID + '" \
                             name="title" \
                             value="" />\
                  </div>\
              ');            
            }
        });
        return showButtons();
    }
    showButtons = function() {
        if (jQuery('.uploadifyQueueItem').length) {
            jQuery('.uploadifybuttons').show();
            return 'ok';
        }
        return false;
    }
    sendDataAndUpload = function() {
        QueueItems = jQuery('.uploadifyQueueItem');
        nbItems = QueueItems.length;
        QueueItems.each(function(i){
            filesData = {};
            ID = jQuery('.file_id_field',this).val();
            filesData['title'] = jQuery('.file_title_field',this).val();
            jQuery('#uploader').uploadifySettings('scriptData', filesData);     
            jQuery('#uploader').uploadifyUpload(ID);       
        })
    }
    onAllUploadsComplete = function(event, data){
        if (!data.errors) {
           Browser.onUploadComplete();
        }
        else {
           msg= data.filesUploaded + '%(ul_msg_some_sucess)s' + data.errors + '%(ul_msg_some_errors)s';
           alert(msg);
        }
    }
    jQuery(document).ready(function() {
        jQuery('#uploader').uploadify({
            'uploader'      : '%(portal_url)s/++resource++plonefinder_static/uploader.swf',
            'script'        : '%(context_url)s/@@finder_upload_file',
            'cancelImg'     : '%(portal_url)s/++resource++plonefinder_static/cancel.png',
            'folder'        : '%(physical_path)s',
            'onAllComplete' : onAllUploadsComplete,
            'auto'          : %(ul_auto_upload)s,
            'multi'         : %(ul_allow_multi)s,
            'simUploadLimit': '%(ul_sim_upload_limit)s',
            'sizeLimit'     : '%(ul_size_limit)s',
            'fileDesc'      : '%(ul_file_description)s',
            'fileExt'       : '%(ul_file_extensions)s',
            'buttonText'    : '%(ul_button_text)s',
            'buttonImg'     : '%(ul_button_image)s',
            'scriptAccess'  : '%(ul_script_access)s',
            'hideButton'    : %(ul_hide_button)s,
            'onSelectOnce'  : addUploadifyFields,
            'scriptData'    : {'ticket' : '%(ticket)s', 'cookie': '%(cookie)s', 'typeupload' : '%(typeupload)s'}
        });
    });
"""

        
class FinderUploadInit(BrowserView):
    """ Initialize uploadify js
    """

    def __init__(self, context, request):
        super(FinderUploadInit, self).__init__(context, request)
        self.context = aq_inner(context)

    def ul_content_types_infos (self, mediaupload):
        """
        return some content types infos depending on mediaupload type
        mediaupload could be 'image', 'video', 'audio' or any
        extension like '*.doc'
        """
        context = aq_inner(self.context)
        ext = '*.*;'
        msg = u'Choose files to upload'
        if mediaupload == 'image' :
            ext = '*.jpg;*.jpeg;*.gif;*.png;'
            msg = u'Choose images to upload'
        elif mediaupload == 'video' :
            ext = '*.flv;*.avi;*.wmv;*.mpg;'
            msg = u'Choose video files to upload'
        elif mediaupload == 'audio' :
            ext = '*.mp3;*.wav;*.ogg;*.mp4;*.wma;*.aif;'
            msg = u'Choose audio files to upload'
        else :
            ext = mediaupload 
            msg = u'Choose file for upload : ' + ext 
        
        return ( ext, self._utranslate(msg))
    
    def _utranslate(self, msg):
        # XXX fixme : the _ (SiteMessageFactory) doesn't work
        context = aq_inner(self.context)
        return context.translate(msg, domain="collective.plonefinder")

    def upload_settings(self):
        context = aq_inner(self.context)
        request = self.request
        session = request.get('SESSION', None)
        
        sp = getToolByName(context, "portal_properties").site_properties
        portal_url = getToolByName(context, 'portal_url')()    
        ticket = ''
        cookie = encode(request.cookies.get('__ac', ''))
        # use a ticket when cookie is empty
        if not cookie :
            ticket = context.restrictedTraverse('@@ticket')()
        
        settings = dict(
            ticket              = ticket,
            cookie              = cookie,
            portal_url          = portal_url,
            typeupload          = '',
            context_url         = context.absolute_url(),
            physical_path       = "/".join(context.getPhysicalPath()),
            ul_auto_upload      = sp.getProperty('ul_auto_upload', 'false'),
            ul_allow_multi      = sp.getProperty('ul_allow_multi', 'true'),
            ul_sim_upload_limit = sp.getProperty('ul_sim_upload_limit', 4),
            ul_size_limit       = sp.getProperty('ul_size_limit', ''),
            ul_button_text      = sp.getProperty('ul_button_text', context.translate(u'Browse', domain="collective.plonefinder")),
            ul_button_image     = sp.getProperty('ul_button_image', ''),
            ul_hide_button      = sp.getProperty('ul_hide_button', 'false'),
            ul_script_access    = sp.getProperty('ul_script_access', 'sameDomain'),
            ul_msg_all_sucess   = self._utranslate( u'All files uploaded with success.'),
            ul_msg_some_sucess   = self._utranslate( u' files uploaded with success, '),
            ul_msg_some_errors   = self._utranslate( u" uploads return an error."),
        )        
        
        mediaupload = session.get('mediaupload', request.get('mediaupload', ''))  
        typeupload = session.get('typeupload', request.get('typeupload', ''))
        settings['typeupload'] = typeupload
        if mediaupload :
            ul_content_types_infos = self.ul_content_types_infos(mediaupload)
        elif typeupload :
            imageTypes = _listTypesForInterface(context, IImageContent)
            if typeupload in imageTypes :
                ul_content_types_infos = self.ul_content_types_infos('image')
        else :
            ul_content_types_infos = (sp.getProperty('ul_file_extensions', '*.*;'),
                                      sp.getProperty('ul_file_description', ''),)
        
        settings['ul_file_extensions'] = ul_content_types_infos[0]
        settings['ul_file_description'] = ul_content_types_infos[1]
            
        return settings

    def __call__(self):
        settings = self.upload_settings()
        return FINDER_UPLOAD_JS % settings        
        

class FinderUploadAuthenticate(BrowserView):
    """
    base view for finder upload authentication
    """
    def __init__(self, context, request):        
        self.context = context
        self.request = request     
        self.cookie = self.request.form.get("cookie")
        if self.cookie :
            self.request.cookies["__ac"] = decode(self.cookie)
            logger.info('Authenticate using plone standard cookie')    
            
    def _auth_with_ticket (self):
        """
        when cookie is empty authentication is done using a ticket
        """
        
        context = aq_inner(self.context)
        request = self.request
        url = context.absolute_url()

        ticket = request.form.get('ticket',None)
        if ticket is None:
            # try to get ticket from QueryString in case of GET method
            qs = request.get('QUERY_STRING','ticket=')
            ticket = qs.split('=')[-1] or None  
        if ticket is None:
            raise Unauthorized('No cookie, and no ticket specified')        
        
        logger.info('Authenticate using ticket, the ticket is "%s"' % str(ticket)) 
        username = ticketmod.ticketOwner(url, ticket)
        if username is None:
            logger.info('Ticket "%s" was invalidated, cannot be used '
                        'any more.' % str(ticket))
            raise Unauthorized('Ticket is not valid')

        self.old_sm = SecurityManagement.getSecurityManager()
        user = find_user(context, username)
        SecurityManagement.newSecurityManager(self.request, user)
        logger.info('Switched to user "%s"' % username)   

        
class FinderUploadFile(FinderUploadAuthenticate):
    """ Upload a file
    """  
                            
    def finder_upload_file(self) :
        
        context = aq_inner(self.context)
        request = self.request        
        if not self.cookie :
            self._auth_with_ticket()         
            
        file_name = request.form.get("Filename", "")
        file_data = request.form.get("Filedata", None)
        content_type = mimetypes.guess_type(file_name)[0]
        portal_type = request.form.get('typeupload', '')
        title =  request.form.get("title", None)
        
        if not portal_type :
            ctr = getToolByName(context, 'content_type_registry')
            portal_type = ctr.findTypeName(file_name.lower(), '', '') or 'File'
        
        if file_data:
            factory = IFileFactory(context)
            logger.info("uploading file: filename=%s, title=%s, content_type=%s, portal_type=%s" % \
                    (file_name, title, content_type, portal_type))                             
            
            f = factory(file_name, title, content_type, file_data, portal_type)
            logger.info("file url: %s" % f.absolute_url())
            
            if not self.cookie :
                SecurityManagement.setSecurityManager(self.old_sm)   
                    
            return f.absolute_url()         
    
    
    def __call__(self):
        """
        """        
        return self.finder_upload_file()  

class FinderUploadCheckFile(BrowserView):
    """
    check if file exists
    """
     

    def finder_upload_check_file(self) :
        
        context = aq_inner(self.context)
        request = self.request          
        url = context.absolute_url()       
        
        always_exist = {}
        formdict = request.form
        ids = context.objectIds()
        
        for k,v in formdict.items():
            if k!='folder' :
                if v in ids :
                    always_exist[k] = v
        
        print '\n\n\n>>>>>%s<<<<<\n\n' %str(always_exist)
        
        return str(always_exist)
    
    
    def __call__(self):
        """
        """        
        return self.finder_upload_check_file()  
        
                             