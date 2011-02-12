# -*- coding: utf-8 -*-
# $Id$
"""Dynamic CSS"""

import os

from App.Common import rfc1123_date
from DateTime import DateTime
from Globals import DTMLFile
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.ResourceRegistries.tools.packer import CSSPacker
from Products.Five import BrowserView


this_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(this_dir, 'dtml')
stylesheet_dtml = DTMLFile('content-types.css', templates_dir)


class TypesCssProperties(BrowserView):
    """properties for content types.css """

    def __call__(self, *args, **kw):
        """Return a dtml file when calling the view"""

        # Wrap acquisition context to template
        context = aq_inner(self.context)
        template = stylesheet_dtml.__of__(context)

        # Push cache headers
        self.setHeader()
        csscontent = template(
            context,
            portal_types_list=self.getPortalTypesList(),
            portal_url=self.getPortalUrl()
            )

        return  CSSPacker('safe').pack(csscontent)


    def getPortalTypesList(self) :
        """List of mappings with 'id' and 'icon' keys
        """
        context = aq_inner(self.context)
        pt_tool = getToolByName(context, 'portal_types')
        plone_utils = getToolByName(context, 'plone_utils')
        normalizeString = plone_utils.normalizeString

        type_info = pt_tool.listTypeInfo()

        # FIXME: Plone provides a vocabulary for user friendly types
        # This hardcoded part is ugly
        excluded_ids = {
            'TempFolder': None,
            'CMF Document': None,
            'CMF Event': None,
            'CMF Favorite': None,
            'CMF File': None,
            'CMF Folder': None,
            'CMF Image': None,
            'CMF Large Plone Folder': None,
            'CMF Link': None,
            'CMF News Item': None,
            'CMF Topic': None,
            'ATCurrentAuthorCriterion': None,
            'ATDateRangeCriterion': None,
            'ATDateCriteria': None,
            'ATListCriterion': None,
            'ATPathCriterion': None,
            'ATPortalTypeCriterion': None,
            'ATReferenceCriterion': None,
            'ATBooleanCriterion': None,
            'ATSelectionCriterion': None,
            'ATSimpleIntCriterion': None,
            'ATSimpleStringCriterion': None,
            'ATSortCriterion': None,
        }

        result = []
        for item in type_info:
            item_id = item.getId()
            if item_id not in excluded_ids:
                result.append({
                    'id': normalizeString(item_id),
                    'icon': item.getIcon(),
                    })

        result.sort(cmp=lambda x, y: cmp(x['id'], y['id']))
        return result


    def getPloneCssProperties(self) :
        """CSS properties based on base_properties
        """
        context = aq_inner(self.context)
        dict_properties = {}
        bp = context.base_properties
        bpdict = bp.propdict()
        for k,v in bpdict.items() :
            if bp.hasProperty(k):
                dict_properties[k] = bp.getProperty(k)

        return dict_properties

    def getPortalUrl(self) :
        """
        return portal url
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.portal_url()


    def setHeader(self):
        """Caching the stylesheet for 20 days
        """
        setHeader = self.request.RESPONSE.setHeader
        setHeader('Content-Type', 'text/css;;charset=utf-8')
        duration = 20 # days
        seconds = float(duration) * 24.0 * 3600.0
        setHeader('Expires', rfc1123_date((DateTime() + duration).timeTime()))
        setHeader('Cache-Control', 'max-age=%d' % int(seconds))
        return

