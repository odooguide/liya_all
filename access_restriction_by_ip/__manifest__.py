{
    'name': 'Access Restriction By IP',
    'version': '18.0.1.0.0',
    'category': 'Extra Tools',
    'summary': """User can be restricted from logging in from different Ip""",
    'description': """This module enhances security by allowing administrators 
     to control user access based on IP addresses. Users will only be able 
     to log in and access their accounts from specified IP addresses, 
     providing an additional layer of protection against unauthorized access.
     """,
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'data': [
        'security/ir.model.access.csv',
        'views/allowed_ips_view.xml'
             ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}

