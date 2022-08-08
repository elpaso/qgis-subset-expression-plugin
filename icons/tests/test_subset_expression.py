# coding=utf-8
""""Test for the subset expression filter plugin

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2022-08-08'
__copyright__ = 'Copyright 2022, ItOpen'


from unittest import TestCase, main, skipIf
from qgis.core import QgsApplication

class RatUtilsTest(TestCase):

    @classmethod
    def setUpClass(cls):

        cls.qgs = QgsApplication([], False)
        cls.qgs.initQgis()

    @classmethod
    def tearDownClass(cls):

        cls.qgs.exitQgis()

    def test_subset_expression(self):
        pass

if __name__ == '__main__':
    main()