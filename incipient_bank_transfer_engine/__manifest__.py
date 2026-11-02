# -*- coding: utf-8 -*-
{
    'name': 'Bank/Cash Transfer Engine',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Creates and posts a balanced pair of journal entries through a configurable transit account to move funds between two bank/cash journals.',
    'description': """
Internal Bank/Cash Transfer Engine
==================================
Creates and posts a balanced pair of journal entries through a configurable transit account 
to move funds between two bank/cash journals, with draft/confirm/reset states.
Standard double-entry logic using only core accounting models - directly portable to any deployment.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': [
        'account','accountant'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/internal_transfer_engine_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 50,
    'currency': 'USD',
}
