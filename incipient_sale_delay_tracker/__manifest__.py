# -*- coding: utf-8 -*-
{
    'name': 'Incipient Sales Delivery Delay Reason Tracker',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Prompts users with a wizard to log delay reasons if confirming a Sales Order past commitment date',
    'author': 'Incipient Corp',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_delay_reason_wizard_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 00,
    'currency': 'USD',
}
