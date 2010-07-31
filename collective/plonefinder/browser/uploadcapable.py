# -*- coding: utf-8 -*-
#
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = 'Ramon Bartl <ramon.bartl@inquant.de>'
__docformat__ = 'plaintext'

import transaction
from thread import allocate_lock
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from Acquisition import aq_inner
from zope import interface
from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.filerepresentation.interfaces import IFileFactory, IDirectoryFactory
from zope.app.container.interfaces import INameChooser
from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFPlone import utils as ploneutils
from Products.CMFCore import utils as cmfutils

from interfaces import IFinderUploadCapable

upload_lock = allocate_lock()


class FinderUploadCapableFileFactory(object):
    interface.implements(IFileFactory)
    component.adapts(IFinderUploadCapable)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, name, title, content_type, data, portal_type):

        context = aq_inner(self.context)
        charset = context.getCharset()
        name = name.decode(charset)
        error = ''
        normalizer = component.getUtility(IIDNormalizer)
        chooser = INameChooser(self.context)
        newid = chooser.chooseName(normalizer.normalize(name), self.context.aq_parent)
        if not title :
            # try to split filenames because we don't want 
            # big titles without spaces
            title = name.split('.')[0].replace('_',' ').replace('-',' ')

        if newid in context.objectIds() :
            raise NameError, 'Object id %s always exist' %newid
        else :
            upload_lock.acquire()
            transaction.begin()
            try:
                context.invokeFactory(type_name=portal_type, id=newid, title=title)
            except Unauthorized : 
                error = 'You are not authorized to upload'
            except ConflictError : 
                error = 'ZODB Conflict Error'
            except :
                error = 'Unknown error during upload'
            if not error :
                obj = getattr(context, newid)
                mutator = obj.getPrimaryField().getMutator(obj)
                mutator(data, content_type=content_type)
                obj.reindexObject()
            transaction.commit()
            upload_lock.release()
        
        if not error :
            return obj
        else :
            raise
        
class FinderCreateFolderCapableFactory(object):
    interface.implements(IDirectoryFactory)
    component.adapts(IFinderUploadCapable)

    def __init__(self, context):
        self.context = aq_inner(context)

    def __call__(self, title, description, portal_type):
        context = aq_inner(self.context)
        charset = context.getCharset()
        title= title.decode(charset)
        description = description.decode("utf8")
        normalizer = component.getUtility(IIDNormalizer)
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

