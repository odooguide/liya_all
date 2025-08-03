{
    "name": "Liya Demo Form",
    "version": "18.0.0.0",
    "category": "Sale",
    "depends": ['project', 'sale', 'sale_management', 'liya_sale_flow', 'crm', 'sale_project'],
    "author": "Broadmax",
    'summary': 'Liya Demo Form',
    "description": """
        Liya Demo Form
	""",
    "website": "https://broadmax.com.tr",
    "data": [
        "views/demo_form.xml",
        "views/project_template_view.xml",
        "views/sale_order_view_inherit.xml",
        "views/sale_order_template_view.xml",
        "views/crm_lead_view_inherit.xml",
        "views/project_task_view_inherit.xml",
        "views/many2many_list_views.xml",
        "wizards/sale_order_project_wizard_view.xml",
        "reports/report_demo_form.xml",
        "security/ir.model.access.csv",
    ],
    "auto_install": False,
    "installable": True,
    "license": "AGPL-3",
}
