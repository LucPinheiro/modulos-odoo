# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Sale Order Client Order Ref Mandatory",
    "summary": """
        Adds required client_order_ref field and reposition it
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/solvosci/slv-sale",
    "depends": ["sale"],
    "data": [        
        "views/sale_order_view.xml",
        "report/sale_order_report_templates.xml",
    ],
    'installable': True,
}
