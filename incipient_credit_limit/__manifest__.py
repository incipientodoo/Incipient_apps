{
    'name': 'Sale Credit Hold',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Put sale orders on credit hold when customer exceeds credit limit',
    'depends': [
        'sale',
        'sale_management',
        'account',
        'stock',
        'mail',
        'incipient_contact_customization',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'wizard/wizard_credit_release_view.xml',
        'views/res_partner.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}