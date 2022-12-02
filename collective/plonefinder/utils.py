# -*- coding: utf-8 -*-
# $Id$
"""Miscellaneous utilities"""

def pleaseDontCache(context, request):
    """Requests the proxy (if any) and user browser to avoid caching the response
    """
    setHeader = request.RESPONSE.setHeader
    setHeader('Content-Type', 'text/html;charset=utf-8')
    setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
    setHeader('Last-Modified', 'Sat, 1 Jan 2000 00:00:00 GMT')
    setHeader('Cache-control', 'max-age=0,s-maxage=0,must-revalidate')
    setHeader('Pragma', 'no-cache')
    return

