# coding=utf-8
""""Subset Expression Plugin

.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

"""

__author__ = 'elpaso@itopen.it'
__date__ = '2022-04-12'
__copyright__ = 'Copyright 2022, ItOpen'


def classFactory(iface):
    """Initialize plugin"""

    from .subsetexpression import SubsetExpression
    return SubsetExpression(iface)
