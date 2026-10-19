# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Website Sale Product Description Extended",
    "summary": """
       Website Sale Product Description Extended.
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/solvosci/slv-e-commerce",
    "application": False,
    "installable": True,
    "depends": ['website_sale'],
    "data": 
        [
         "views/website_sale_template.xml",
         "views/product_template.xml",
        ],
     "demo": [
        "data/demo_website_sale_product_description.xml",
    ],
}
