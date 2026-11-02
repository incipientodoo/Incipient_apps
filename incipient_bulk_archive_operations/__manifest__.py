# -*- coding: utf-8 -*-
{
    'name': 'Bulk Archive Routing Operations & Orphan Cleanup',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Bulk-archive BOM routing operations and automatically clean up orphaned quality points.',
    'description': """
Bulk Archive Routing Operations & Orphan Cleanup
=================================================
A wizard to bulk-select and archive BOM routing operations.
It automatically removes/archives quality check points that become orphaned as a result.
Generic routing-maintenance/cleanup mechanism with no sign-specific logic.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': [
        'mrp_workorder','quality_control'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/archive_operations_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 50,
    'currency': 'USD',
}
