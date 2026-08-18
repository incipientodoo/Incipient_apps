# -*- coding: utf-8 -*-
{
    'name': 'Customize Fiscal Year-Quarters',
    'version': '19.0.1.0.0',
    'category': 'Tools',
    'summary': 'Extend fiscal year configurations with intelligent quarter-based views and reporting—fully aligned across all filters and group by fields.',
    'description': """
Extend Fiscal Year and Quarter Grouping & Filtering (Odoo 19)
=============================================================
Extends fiscal year configurations with quarter-based views, group by, and reporting
aligned across date filters and group by options based on company fiscal year settings.
    """,
    'author': 'Incipient Corp',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'base_setup',
        'accountant',
        'web',
    ],
    'assets': {
        'web.assets_backend': [
            'incipient_customize_fiscal_year_and_quarter/static/src/search/custom_date.js',
            'incipient_customize_fiscal_year_and_quarter/static/src/js/dates.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 100,
    'currency': 'USD',
}
