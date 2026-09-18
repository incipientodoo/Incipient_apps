# -*- coding: utf-8 -*-
{
    'name': 'Sale BOM & MRP Checks',
    'version': '19.0.1.0.0',
    'category': 'Sale',
    'summary': """Sale BOM & MRP Checks module checks required engineering data when confirming a Sales Order.
    It prevents confirmation if a product is missing a BoM, Operations, or required attachments, and sends an alert to the Engineering team.""",
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['sale_management', 'mrp'],
    'data': [
        'security/security.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 0,
    'currency': 'USD',
}
