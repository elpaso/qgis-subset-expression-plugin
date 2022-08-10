# -*- coding: utf-8 -*-
""""Subset Expression Plugin

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2022-04-12'
__copyright__ = 'Copyright 2022, ItOpen'

import os
import re
import inspect
from functools import partial

from qgis.core import Qgis, QgsApplication, QgsProject, QgsMapLayerType

# Import the code for the dialog
from .widgetfactory import SubsetExpressionWidgetFactory
from .utils import set_subset_expression, get_subset_expression, notify, _tr


class SubsetExpression(object):

    def __init__(self, iface):

        self.iface = iface
        QgsProject.instance().readProject.connect(self.load_subsets)
        self.factory = SubsetExpressionWidgetFactory(iface, _tr("Layer filter expressions"), QgsApplication.getThemeIcon("/mActionFilter2.svg"))
        iface.registerProjectPropertiesWidgetFactory(self.factory)
        QgsApplication.instance().customVariablesChanged.connect(self.var_changed)
        QgsProject.instance().customVariablesChanged.connect(self.var_changed)
        QgsProject.instance().customVariablesChanged.connect(self.var_changed)
        QgsProject.instance().layersAdded.connect(self.connect_layers)

    def unload(self):

        self.iface.unregisterProjectPropertiesWidgetFactory(self.factory)
        QgsApplication.instance().customVariablesChanged.disconnect(self.var_changed)
        QgsProject.instance().customVariablesChanged.disconnect(self.var_changed)

    def load_subsets(self, dom=None):

        for layer in QgsProject.instance().mapLayers().items():
            layer = layer[1]
            exp_text = layer.customProperty('subset_expression')
            exp_checked = layer.customProperty('subset_expression_checked', 0) == 1
            if exp_checked:
                set_subset_expression(layer, exp_text, self.iface)

    def var_changed(self):

        self.load_subsets()

    def initGui(self):

        pass

    def connect_layers(self, layers):

        for l in layers:
            if l.type() == QgsMapLayerType.VectorLayer:
                l.subsetStringChanged.connect(partial(self.check_manual_override, l))

    def check_manual_override(self, layer):

        current_subset_expression = get_subset_expression(layer)
        if current_subset_expression != '':
            if layer.subsetString() != current_subset_expression:
                layer.setCustomProperty('subset_expression_checked', 0)
                notify(self.iface, _tr("Warning"), _tr("The dynamic provider filter for layer <b>{}</b> has been disabled because it was manually overridden to <tt>{}</tt>)".format(layer.name(), layer.subsetString())), level=Qgis.Warning)


if __name__ == "__main__":
    pass
