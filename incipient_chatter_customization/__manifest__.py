{
    'name': 'Chatter Customization',
    'version': '19.0.1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Configure Chatter behavior per user and model',
    'description': """
        This module allows administrators to configure Chatter behavior per user and per model.
        Features:
        - Hide the "Send Message" button for selected users on selected models.
        - Add a Collapse/Expand toggle for the Chatter panel on record forms.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/chatter_config_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'incipient_chatter_customization/static/src/chatter.scss',
            'incipient_chatter_customization/static/src/chatter_patch.js',
            'incipient_chatter_customization/static/src/chatter_patch.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 60,
    'currency': 'USD',
}
