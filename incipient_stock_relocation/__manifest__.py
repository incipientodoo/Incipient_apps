# -*- coding: utf-8 -*-
{
    'name': 'Lot & Receipt-Based Internal Stock Relocation Wizards',
    'version': '19.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Wizards to relocate specific lot quantity and distribute purchase receipt lines to multiple locations.',
    'description': """
Lot & Receipt-Based Internal Stock Relocation Wizards
=====================================================
- Move a specific lot's quantity between locations validating available quantity.
- Distribute a purchase receipt's lines across arbitrary destination locations into grouped pickings.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': [
        'stock',
        'purchase',
        'mrp',
        'purchase_stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/wizard_lot_relocate_views.xml',
        'views/wizard_receipt_distribute_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 90,
    'currency': 'USD',
}
