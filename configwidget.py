# coding=utf-8
""""Plugin config widget

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2022-05-10'
__copyright__ = 'Copyright 2022, ItOpen'


import os
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTableWidgetItem, QCheckBox
from qgis.gui import QgsOptionsPageWidget
from qgis.core import QgsProject, QgsMapLayerType

from .utils import set_subset_expression, _tr

class ConfigWidget(QgsOptionsPageWidget):
    """Configuration widget for filter expressions"""

    def __init__(self, iface, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(
            __file__), 'Ui_ConfigWidget.ui')
        uic.loadUi(ui_path, self)
        self.layout().setContentsMargins(0,0,0,0)
        self.iface = iface

        vector_layers =  [l for l in list(QgsProject.instance().mapLayers().values()) if l.type() == QgsMapLayerType.VectorLayer]
        self.mLayerTableWidget.setRowCount(len(vector_layers))
        self.mLayerTableWidget.setColumnCount(4)
        self.mLayerTableWidget.setHorizontalHeaderLabels([_tr('Active'), _tr('Name'), _tr('Filter expression'), _tr('Current expression')])
        self.mLayerTableWidget.setColumnWidth(1, 200)
        self.mLayerTableWidget.setColumnWidth(2, 500)
        self.mLayerTableWidget.setColumnWidth(3, 500)

        self.mToggleAllButton.clicked.connect(self.toggle_all)

        for row in range(len(vector_layers)):
            l = vector_layers[row]
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Checked if l.customProperty('subset_expression_checked', 0) == 1 else Qt.Unchecked)
            name_item = QTableWidgetItem(l.name())
            name_item.setFlags(Qt.NoItemFlags)
            filter_subset_item = QTableWidgetItem(l.subsetString())
            filter_subset_item.setFlags(Qt.NoItemFlags)
            subset_item = QTableWidgetItem(l.customProperty('subset_expression', l.subsetString()))
            self.mLayerTableWidget.setItem(row, 0, check_item)
            self.mLayerTableWidget.setItem(row, 1, name_item)
            self.mLayerTableWidget.setItem(row, 2, subset_item)
            self.mLayerTableWidget.setItem(row, 3, filter_subset_item)

        self.vector_layers =  vector_layers

    def apply(self):

        for row in range(len(self.vector_layers)):
            exp_checked = 1 if self.mLayerTableWidget.item(row, 0).checkState() == Qt.Checked else 0
            exp_text = self.mLayerTableWidget.item(row, 2).data(Qt.DisplayRole).strip()
            layer_instance = self.vector_layers[row]
            layer_instance.setCustomProperty('subset_expression', exp_text)
            layer_instance.setCustomProperty('subset_expression_checked', exp_checked)
            if exp_checked:
                set_subset_expression(layer_instance, exp_text, self.iface)

    def toggle_all(self):
        """Toggle all layers"""

        for row in range(self.mLayerTableWidget.rowCount()):
            item = self.mLayerTableWidget.item(row, 0)
            item.setCheckState(Qt.Unchecked if item.checkState() == Qt.Checked else Qt.Unchecked)


