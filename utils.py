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


def set_subset_expression(layer_instance, exp_text, iface) -> bool:
    """Set the subset expression on the layer instance

    :param layer_instance: layer instance
    :type layer_instance: vector layer
    :param exp_text: expression text
    :type exp_text: str
    :param iface: QGIS interface
    :type iface: iface
    :return: True on success
    :rtype: bool
    """

    if exp_text is not None and exp_text != "":
        ctx = QgsExpressionContext(QgsExpressionContextUtils.globalProjectLayerScopes(layer_instance))

        # Validate
        var_list = re.findall(r'@(\w+)', exp_text)
        for exp_var in var_list:
            if not ctx.hasVariable(exp_var):
                iface.messageBar().pushMessage(_tr("Notice"), _tr("Layer <b>{}</b> dynamic filter <tt>{}</tt> is invalid: variable <tt>@{}</tt> is not defined! Filter was not set.").format(layer_instance.name(), exp_text,
                exp_var), level=Qgis.Warning)
                return False

        for var in var_list:
            exp_text = exp_text.replace('@{}'.format(var), str(ctx.variable(var)))

        if exp_text == layer_instance.subsetString():
            log_message(_tr("Layer <b>{}</b> was not changed.").format(layer_instance.name()))
            return False

        if layer_instance.setSubsetString(exp_text):
            iface.messageBar().pushMessage(_tr("Notice"), _tr("Layer <b>{}</b> dynamically filtered: <tt>{}</tt>)").format(layer_instance.name(), exp_text), level=Qgis.Success)
            return True
        else:
            iface.messageBar().pushMessage(_tr("Error"), _tr("Error setting dynamic filter for layer <b>{}</b> to <tt>{}</tt>)"), level=Qgis.Critical)
            return False

    return False
