# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Purchase Order Partner Ref Mandatory",
    "summary": """
        Adds Partner Ref Mandatory in purchase order
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.1.0",
    "category": "Purchase",
    "website": "https://github.com/solvosci/slv-purchase",
    "depends": [
        "purchase",
    ],
    "data": [
        "views/purchase_order_views.xml",
    ],
    'installable': True,
}
