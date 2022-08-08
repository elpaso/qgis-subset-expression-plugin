# coding=utf-8
""""Widget factory for plugin configuration

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2022-05-10'
__copyright__ = 'Copyright 2022, ItOpen'


from qgis.core import QgsApplication
from qgis.gui import QgsOptionsWidgetFactory

from .configwidget import ConfigWidget

class SubsetExpressionWidgetFactory(QgsOptionsWidgetFactory):

    def __init__(self, iface, title, icon):
        super().__init__(title, icon)
        self.iface = iface

    def createWidget(self, parent=None):
        return ConfigWidget(self.iface, parent)

