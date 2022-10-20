# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@inquant.de>'
__docformat__ = 'plaintext'

import transaction
from _thread import allocate_lock
from Acquisition import aq_inner
from zope.interface import implementer
from zope.component import adapter
from zope.component import getUtility
from zope.filerepresentation.interfaces import IDirectoryFactory
from zope.container.interfaces import INameChooser

from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFPlone import utils as ploneutils

from collective.plonefinder.browser.interfaces import IFinderUploadCapable

upload_lock = allocate_lock()


@implementer(IDirectoryFactory)
@adapter(IFinderUploadCapable)
class FinderCreateFolderCapableFactory(object):

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, title, description, portal_type):
        context = aq_inner(self.context)
        charset = context.getCharset()
        title = title.decode(charset)
        description = description.decode("utf8")
        normalizer = getUtility(IIDNormalizer)
        chooser = INameChooser(self.context)
        newid = chooser.chooseName(normalizer.normalize(title), self.context.aq_parent)

        # otherwise I get ZPublisher.Conflict ConflictErrors
        # when uploading multiple files
        upload_lock.acquire()
        try:
            transaction.begin()
            obj = ploneutils._createObjectByType(portal_type, self.context, newid)
            obj.setTitle(title)
            obj.setDescription(description)
            obj.reindexObject()
            transaction.commit()
        finally:
            upload_lock.release()
        return obj

