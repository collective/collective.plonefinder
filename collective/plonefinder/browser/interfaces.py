# -*- coding: utf-8 -*-
# $Id$

from zope.interface import Interface

# FIXME: Why is this a marker interface

class IFinderUploadCapable(Interface):
    """Any container/object which supports uploading through plone_finder.
    """


