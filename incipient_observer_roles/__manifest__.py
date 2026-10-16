# -*- coding: utf-8 -*-
{
    'name': 'Incipient View-Only Observer Roles for Sales & Purchase',
    'version': '19.0.1.0.0',
    'category': 'Sales/Purchasing',
    'summary': 'Dedicated read-only auditor/observer security roles for Sales and Purchasing workflows',
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['sale_management', 'purchase', 'stock', 'account', 'mrp', 'spreadsheet_sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 0,
    'currency': 'USD',
}
