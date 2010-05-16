"""Main product initializer
"""

import logging
from zope.i18nmessageid import MessageFactory
logger = logging.getLogger("collective.plonefinder")

siteMessageFactory = MessageFactory("collective.plonefinder")

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

