# -*- coding: utf-8 -*-
{
    'name': 'Incipient Per-Product Dual Approval Gate on Sales Orders',
    'version': '19.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Enforce Customer Sign-Off and/or Sales Manager Approval on SOs containing restricted products',
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['sale_management', 'stock', 'sale_stock'],
    'data': [
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 50,
    'currency': 'USD',
}
