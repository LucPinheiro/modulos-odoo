# © 2023 LuoDoo, Desarrollo de soluciones tecnólogicas (<http://www.luodoo.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)
{
    "name": "Website Product Price",
    "summary": """
        Website Contacts CRM"
    """,
    "author": "Solvos",
    "license": "AGPL-3",
    "version": "15.0.1.0.0",
    "category": "Sale",
    "website": "https://github.com/solvosci/slv-website",
    "depends": ['website_sale'],
    "data":  ['data/product_snippet_template_data.xml'],
    "installable": True,
        "assets": {
        'web.assets_frontend': [
            'website_contacts_crm/static/src/js/form_editor_registry.js',
        ],
    },
}
