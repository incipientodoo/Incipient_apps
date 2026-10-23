{
    'name': 'Incipient Purchase Email & Chatter Alert System',
    'version': '19.0.1.0.0',
    'category': 'Purchasing',
    'summary': 'Configurable PO change, unit price increase, and receipt confirmation email/chatter alerts',
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['purchase', 'stock', 'purchase_stock', 'mail'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 30,
    'currency': 'USD',
}
