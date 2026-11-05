# -*- coding: utf-8 -*-
{
    'name': 'Inventory Receipt Timer',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Adds start/stop timers to incoming receipts, auto-provisioning a linked task and writing time to timesheet.',
    'description': """
        Adds start/stop timers to incoming receipts, auto-provisioning a linked task on first use, 
        enforcing one active timer per user, and writing the resulting time back as a timesheet entry.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': [
        'stock',
        'project',
        'hr_timesheet',
    ],
    'data': [
        'views/project_project_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 50,
    'currency': 'USD',
}
