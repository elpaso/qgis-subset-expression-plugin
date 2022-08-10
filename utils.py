# coding=utf-8
""""Filter Expression Utils

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2022-05-12'
__copyright__ = 'Copyright 2022, ItOpen'

import re
from qgis.core import (
    QgsExpressionContextUtils,
    QgsExpressionContext,
    QgsMessageLog,
    Qgis,
)

PLUGIN_DOMAIN = 'Subset Filter Plugin'


from qgis.PyQt.QtCore import QCoreApplication

def _tr(s):
    """Translate, save some typing"""

    return QCoreApplication.translate(PLUGIN_DOMAIN, s)

def log_message(message, level=Qgis.MessageLevel.Info):
    """Log a message

    :param message: message text
    :type message: str
    :param level: log level, defaults to Qgis.MessageLevel.Info
    :type level: int, optional
    """

    QgsMessageLog.logMessage(message, PLUGIN_DOMAIN, level)

def get_subset_expression(layer) -> str:
    """Calculate the subset expression for the layer, an empty string is returned
    if the subset string could not be calculated or it is disabled

    :param layer: the layer
    :type layer: QgsVectorLayer
    :return: the calculated subset string or an empty string
    :rtype: str
    """

    if layer.customProperty('subset_expression_checked'):

        exp_text = layer.customProperty('subset_expression')

        if exp_text is not None and exp_text != "":
            ctx = QgsExpressionContext(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

            # Validate
            var_list = re.findall(r'@(\w+)', exp_text)
            for exp_var in var_list:
                if not ctx.hasVariable(exp_var):
                    return ''

            for var in var_list:
                exp_text = exp_text.replace('@{}'.format(var), str(ctx.variable(var)))

            return exp_text

    return ''


def notify(iface, title, message, level=Qgis.Info):
    """Push message on message bar and log it"""

    iface.messageBar().pushMessage(title, message, level)
    log_message(message, level)

def set_subset_expression(layer, exp_text, iface) -> bool:
    """Set the subset expression on the layer instance

    :param layer: layer instance
    :type layer: vector layer
    :param exp_text: expression text
    :type exp_text: str
    :param iface: QGIS interface
    :type iface: iface
    :return: True on success
    :rtype: bool
    """

    if exp_text is not None and exp_text != "":

        ctx = QgsExpressionContext(QgsExpressionContextUtils.globalProjectLayerScopes(layer))

        # Validate
        var_list = re.findall(r'@(\w+)', exp_text)
        for exp_var in var_list:
            if not ctx.hasVariable(exp_var):
                notify(iface, _tr("Notice"), _tr("Layer <b>{}</b> dynamic provider filter definition <tt>{}</tt> is invalid: variable <tt>@{}</tt> is not defined! Provider filter was not changed.").format(layer.name(), exp_text,
                exp_var), level=Qgis.Warning)
                return False

        for var in var_list:
            exp_text = exp_text.replace('@{}'.format(var), str(ctx.variable(var)))

        if exp_text == layer.subsetString():
            return False

        if layer.setSubsetString(exp_text):
            notify(iface, _tr("Notice"), _tr("Layer <b>{}</b> provider filter was changed to: <tt>{}</tt>").format(layer.name(), exp_text), level=Qgis.Success)
            return True
        else:
            notify(iface, _tr("Error"), _tr("Error setting provider filter for layer <b>{}</b> to <tt>{}</tt>").format(layer.name(), exp_text), level=Qgis.Critical)
            return False

    return False

def store_subset_expression(layer, exp_text, exp_checked, iface) -> bool:
    """Store the filter expression text in the project

    :param layer: vector layer
    :type layer: QgsVectorLayer
    :param exp_text: expression text
    :type exp_text: str
    :param exp_checked: expression is checked
    :type exp_cheked: bool
    :param iface: QGIS interface
    :type iface: iface
    :return: True on success
    :rtype: bool
    """

    layer.setCustomProperty('subset_expression', exp_text)
    layer.setCustomProperty('subset_expression_checked', exp_checked)

    if exp_checked:
        return set_subset_expression(layer, exp_text, iface)

    return True