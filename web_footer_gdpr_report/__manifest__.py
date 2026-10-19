# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Web Footer GDPR Report",
    "summary": """
        Adds footer GDPR report in layout web
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Sales/Sales",
    "website": "https://github.com/solvosci/slv-sale",
    "depends": [
        "sale","web"
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "report/web_footer_gdpr_report.xml"
    ],
    'installable': True,
}
