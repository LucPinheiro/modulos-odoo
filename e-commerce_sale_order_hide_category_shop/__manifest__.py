# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "e-commerce_sale_order_hide_category_shop",
    "summary": """
       e-commerce_sale_order_hide_category_shop.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "16.0.1.0.0",
    "category": "E-commerce",
    "website": "https://github.com/solvosci/e-commerce",
    "depends": ['website_sale'],
    "data": 
        [
        "views/templates.xml",
        ],
    "assets": {
        'web.assets_frontend': [
            'e-commerce_sale_order_hide_category_shop/static/src/scss/website_sale.scss',
        ],
    },
    "installable": True,
}
