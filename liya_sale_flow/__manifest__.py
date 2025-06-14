{
    "name": "Liya Sale Flow",
    "version": "18.0.0.0",
    "category": "Sale",
    "depends": [ 'sale',  'crm','base','sale_management','project','mail'],
    "author": "Broadmax",
    'summary': 'Liya Sale Flow',
    "description": """
        Liya Sale Flow
	""",
    "website": "https://broadmax.com.tr",
    "data": [
        "views/crm_lead.xml",
        "views/sale_order_template_view.xml",
        "views/sale_order_view_inherit.xml",
        "security/ir.model.access.csv",
        "reports/report_saleorder_document_inherit.xml",
        "data/ir_sequence.xml",
        "data/calendar_alarm_data.xml",
        "views/mail_activity_type.xml",
    ],
    "auto_install": False,
    "installable": True,
}