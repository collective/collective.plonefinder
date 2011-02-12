# -*- coding: utf-8 -*-
# $Id$
"""Main product initializer
"""

import logging
from zope.i18n import MessageFactory
from collective.plonefinder import config

logger = logging.getLogger(config.PROJECTNAME)
siteMessageFactory = MessageFactory(config.PROJECTNAME)


