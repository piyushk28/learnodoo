# -*- coding: utf-8 -*-
{
    'name': "Recycle Module",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpodependenciesse
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/flectra/flectra/blob/12.0/flectra/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_stock','product','account','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/recycle_menu.xml',
        'views/views.xml',
        'views/templates.xml',
        'reports/recycle_report.xml',
        'reports/inbound_order_quotation_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application':False,
    'auto_install':False
}