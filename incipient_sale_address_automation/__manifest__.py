# -*- coding: utf-8 -*-
{
    'name': 'Billing & Shipping Address Automation',
    'version': '19.0.1.0.0',
    'category': 'Sale',
    'summary': 'Automates Billing and Shipping Addresses on Sale Orders',
    'description': """
        This module automates the selection of billing and shipping addresses on Sale Orders.
        When a Sale Order is linked to an Opportunity, it automatically computes and sets the 
        delivery and invoice addresses based on the customer's defined address types, ensuring 
        accurate addressing for orders originating from CRM.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['sale_crm', 'account', 'sale_management', 'stock', 'sale_stock'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'currency': 'USD',
}
