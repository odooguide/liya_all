{
    "name": "Liya Demo Form",
    "version": "18.0.0.0",
    "category": "Sale",
    "depends": [ 'project','sale','sale_management'],
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
        "security/ir.model.access.csv",
    ],
    "auto_install": False,
    "installable": True,
    "license": "AGPL-3",
}