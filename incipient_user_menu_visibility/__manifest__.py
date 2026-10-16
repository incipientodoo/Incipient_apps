# -*- coding: utf-8 -*-
{
    'name': 'Incipient Per-User Menu Visibility Control',
    'version': '19.0.1.0.0',
    'category': 'Administration',
    'summary': 'Hide specific menu items and their sub-menus per user with automated cleanup',
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['base', 'web'],
    'data': [
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 30,
    'currency': 'USD',
}
