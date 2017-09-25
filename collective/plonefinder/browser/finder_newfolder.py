# -*- coding: utf-8 -*-
# $Id$

"""UI for creating a new folder"""

# Code taken from collective.uploadify for the base of the logic with some
# improvements. Use the ticket.py from PloneFlashUpload to avoid
# authentification problems with flash upload form

from Acquisition import aq_inner
from collective.plonefinder import logger
from collective.plonefinder.utils import pleaseDontCache
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FinderNewFolderView(BrowserView):
    """Create folder form
    """

    template = ViewPageTemplateFile('finder_newfolder.pt')

    def __call__(self):
        """Publishing the view through browser
        """
        pleaseDontCache(self.context, self.request)
        # Render
        return self.template()


class FinderNewFolder(BrowserView):
    """Create a folder
    """
    def __call__(self):
        """Publishing the view through browser
        """
        return self.create_folder()


    def create_folder(self):
        """Creating the folder
        """
        context = aq_inner(self.context)
        request = self.request
        session = request.get('SESSION', None)

        # FIXME: hardcoded content type, should be in config.py
        portal_type = session.get('typefolder', request.get('typefolder', 'Folder'))

        title = request.get('folder-title', '')
        description = request.get('folder-description', '')

        logger.info('creating folder: title=%s, description=%s, portal_type=%s',
                    title, description, portal_type)

        f = api.content.create(
            type=portal_type,
            container=context,
            title=title,
            description=description)

        logger.info("folder url: %s" % f.absolute_url())

        return f.absolute_url()
