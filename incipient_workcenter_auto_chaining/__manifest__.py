{
    'name': 'Workcenter Auto Start/Stop Chaining',
    'version': '19.0.1.0.0',
    'summary': 'Configurable links between workcenters for auto-starting/stopping work orders',
    'description': """
        This module provides configurable links between workcenters. 
        Finishing a work order on one workcenter automatically starts or stops linked workcenters.
        It also includes a cron job that auto-finishes work orders once their expected duration elapses.
    """,
    'category': 'Manufacturing/Manufacturing',
    'author': 'Incipient Corp',
    'website': 'www.incipientcorp.com',
    'license': 'OPL-1',
    'depends': ['mrp', 'mrp_workorder'],
    'data': [
        'views/mrp_workcenter_views.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'images': ['static/description/banner.gif'],
    'price': 50,
    'currency': 'USD',
}
