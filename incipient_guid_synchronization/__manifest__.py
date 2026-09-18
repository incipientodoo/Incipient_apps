# -*- coding: utf-8 -*-
{
    'name': 'GUID Synchronization',
    'version': '19.0.1.0.0',
    'category': 'Sale',
    'summary': 'Establishes a GUID synchronization mechanism generating unique tracking GUIDs across multiple models.',
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['base', 'sale', 'purchase', 'account', 'crm','sale_management'],
    'data': [
        'security/security.xml',
        'views/guid_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 0,
    'currency': 'USD',
}
