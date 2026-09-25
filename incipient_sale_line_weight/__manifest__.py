# -*- coding: utf-8 -*-
{
    'name': 'Line & Section Weight Calculations',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Calculates unit weight and extended weight on sales and invoice lines based on quantities.',
     'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['sale_management', 'account'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_report.xml',
        'views/account_move_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 30,
    'currency': 'USD',
}
