# -*- coding: utf-8 -*-
import unittest
from plone import api

from ..testing import COLLECTIVE_PLONEFINDER_INTEGRATION


class TestPlonefinder(unittest.TestCase):

    layer = COLLECTIVE_PLONEFINDER_INTEGRATION

    def test_view_basic(self):
        portal = self.layer['portal']
        view = portal.restrictedTraverse('@@plone_finder')
        contents = view()
        self.assertTrue('plone-browser' in contents)

