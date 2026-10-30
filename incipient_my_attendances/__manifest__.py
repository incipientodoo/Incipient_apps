# -*- coding: utf-8 -*-
{
    'name': 'My Attendances (Self-Service)',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Attendances',
    'summary': 'Standalone My Attendances Self-Service Screen with Check-In/Check-Out',
    'description': """
My Attendances (Self-Service)
=============================
Provides a standalone, generic self-service screen for employees to view their own attendance 
status and perform Check-In/Check-Out operations.
    """,
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['hr_attendance', 'web'],
    'data': [
        'views/attendance_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'incipient_my_attendances/static/src/my_attendances.js',
            'incipient_my_attendances/static/src/my_attendances.xml',
            'incipient_my_attendances/static/src/my_attendances.scss',
        ],
    },
     'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 40,
    'currency': 'USD',
}
