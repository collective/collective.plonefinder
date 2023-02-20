# -*- coding: utf-8 -*-
import unittest
from plone import api

from ..testing import COLLECTIVE_PLONEFINDER_INTEGRATION


class TestPlonefinder(unittest.TestCase):

    layer = COLLECTIVE_PLONEFINDER_INTEGRATION

    def test_dummy(self):
        self.assertTrue(True)
