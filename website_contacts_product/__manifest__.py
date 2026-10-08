# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)
{
    "name": "Website Contacts Product",
    "summary": """
        Website Contacts Product"
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "16.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/solvosci/slv-website",
    "depends": ['website','website_sale_stock'],
    "data":  ['data/website_data.xml'],
    "installable": True,
    "assets": {
        'web.assets_editor': [
            'website_contacts_product/static/src/js/form_editor_registry.js',
        ],
    },
}
