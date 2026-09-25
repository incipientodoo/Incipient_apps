{
    'name': 'Sales Order Approval & Discount Control Flow',
    'version': '19.0.1.0.0',
    'category': 'Sale',
    'summary': 'Extends Sale Order states and approval sequences',
    'description': """
        - Extends Sale Order states to include custom approval stages.
        - Restricts validation and forces an approval sequence if the extra discount offered is > 5%.
        - Payment terms are configured as read-only based on custom group permissions.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['sale_management'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 40,
    'currency': 'USD',
}
