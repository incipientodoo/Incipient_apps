# -*- coding: utf-8 -*-
{
    'name': 'Incipient CRM Lead Analytics',
    'version': '19.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'CRM pipeline analytics buckets, cycle times, and neglected lead tracker',
    'author': 'Incipient Corp',
    'license': 'LGPL-3',
    'depends': ['crm', 'mail'],
    'data': [
        'data/cron_jobs.xml',
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 00,
    'currency': 'USD',
}
