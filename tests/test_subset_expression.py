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

import os
import sys
import importlib.util
from pathlib import Path
from osgeo import ogr
from unittest import main
from qgis.core import QgsVectorLayer, QgsProject, QgsExpressionContextUtils
from qgis.PyQt.QtCore import QTemporaryDir
from qgis.testing import TestCase, start_app
from qgis.testing.mocked import get_iface
from qgis import utils as qgis_utils

sys.path.append(
    str(Path(os.path.dirname(__file__)).parent.absolute().parent.absolute()))

QGISAPP = start_app()


class SubsetExpressionUtilsTest(TestCase):

    @classmethod
    def setUpClass(cls):

        cls.iface = get_iface()
        qgis_utils.plugin_paths = [
            str(Path(os.path.dirname(__file__)).parent.absolute().parent.absolute())]
        qgis_utils.updateAvailablePlugins()
        result = qgis_utils.loadPlugin('qgis-subset-expression-plugin')
        assert result
        package = sys.modules['qgis-subset-expression-plugin']
        qgis_utils.plugins['qgis-subset-expression-plugin'] = package.classFactory(
            cls.iface)
        assert result
        cls.package = package

        spec = importlib.util.spec_from_file_location(
            "utils", os.path.join(package.__path__[0], "utils.py"))
        utils = importlib.util.module_from_spec(spec)
        sys.modules["utils"] = utils
        globals()['utils'] = utils
        spec.loader.exec_module(utils)

    @classmethod
    def tearDownClass(cls):

        pass

    def setUp(self):
        """Prepare test data and project"""

        self.tmp_dir = QTemporaryDir()
        self.temp_path = os.path.join(
            self.tmp_dir.path(), 'subset_expression_test.gpkg')
        self.temp_project_path = os.path.join(
            self.tmp_dir.path(), 'subset_expression_test.qgs')

        ds = ogr.GetDriverByName('GPKG').CreateDataSource(self.temp_path)
        lyr = ds.CreateLayer('test_layer', geom_type=ogr.wkbNone)
        lyr.CreateField(ogr.FieldDefn('name', ogr.OFTString))
        f = ogr.Feature(lyr.GetLayerDefn())
        f['name'] = 'A1'
        lyr.CreateFeature(f)
        f = ogr.Feature(lyr.GetLayerDefn())
        f['name'] = 'B1'
        lyr.CreateFeature(f)
        f = ogr.Feature(lyr.GetLayerDefn())
        f['name'] = 'A2'
        lyr.CreateFeature(f)

        f = None
        ds = None

        test_layer = QgsVectorLayer(
            self.temp_path + '|layername=test_layer', 'test_layer')
        QgsProject.instance().addMapLayers([test_layer])
        self.layer = test_layer

        # Save the project
        QgsProject.instance().write(self.temp_project_path)

    def test_subset_expression(self):

        self.assertEqual(set([f['name'] for f in self.layer.getFeatures()]), {
                         'A1', 'A2', 'B1'})
        utils.store_subset_expression(self.layer, "name LIKE '@first_letter%'", True, self.iface)  # noqa: F821

        # There is no variable set, no expression is set
        self.assertEqual(set([f['name'] for f in self.layer.getFeatures()]), {
                         'A1', 'A2', 'B1'})

        # Set the expression at project level
        QgsExpressionContextUtils.setProjectVariable(
            QgsProject.instance(), 'first_letter', 'A')
        self.assertEqual(set([f['name']
                              for f in self.layer.getFeatures()]), {'A1', 'A2'})

        QgsExpressionContextUtils.setGlobalVariable('first_letter', 'B')
        # No changes so far: project has precedence
        self.assertEqual(set([f['name']
                              for f in self.layer.getFeatures()]), {'A1', 'A2'})

        # Now we get B!
        QgsExpressionContextUtils.removeProjectVariable(
            QgsProject.instance(), 'first_letter')
        self.assertEqual(set([f['name']
                              for f in self.layer.getFeatures()]), {'B1'})

        # Clear, no var, no changes!
        QgsExpressionContextUtils.removeGlobalVariable('first_letter')
        self.assertEqual(set([f['name']
                              for f in self.layer.getFeatures()]), {'B1'})

    def test_subset_string_override(self):
        """Test if a user-overridden subset takes precedence"""

        QgsExpressionContextUtils.setGlobalVariable('first_letter', 'B')
        self.assertEqual(set([f['name'] for f in self.layer.getFeatures()]), {
                         'A1', 'A2', 'B1'})

        self.assertFalse(self.layer.customProperty('subset_expression_checked'))
        utils.store_subset_expression(self.layer, "name LIKE '@first_letter%'", True, self.iface)  # noqa: F821
        self.assertEqual(set([f['name'] for f in self.layer.getFeatures()]), {'B1'})

        # Check if rule is enabled
        self.assertTrue(self.layer.customProperty('subset_expression_checked'))

        # Manual override
        self.layer.setSubsetString('name LIKE \'A%\'')
        self.assertEqual(set([f['name'] for f in self.layer.getFeatures()]), {
                         'A1', 'A2'})
        # Check if rule was disabled
        self.assertFalse(self.layer.customProperty('subset_expression_checked'))



if __name__ == '__main__':
    main()
