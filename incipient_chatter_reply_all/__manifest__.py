# -*- coding: utf-8 -*-
{
    'name': 'Chatter Reply All',
    'version': '19.0.1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Add a Reply All action to Odoo Chatter messages to automatically mention the author and previously mentioned users.',
    'description': """
Chatter Reply All (Odoo 19)
===========================
Adds a "Reply All" action to Odoo Chatter messages. When clicked, it opens the Log Note composer
and automatically pre-fills mentions (@) for the original message's author and any previously mentioned users.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': [
        'mail',
        'web',
        'sale_management'
    ],
    'assets': {
        'web.assets_backend': [
            'incipient_chatter_reply_all/static/src/core/common/composer_model_patch.js',
            'incipient_chatter_reply_all/static/src/core/common/message_actions_patch.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 40,
    'currency': 'USD',
}
