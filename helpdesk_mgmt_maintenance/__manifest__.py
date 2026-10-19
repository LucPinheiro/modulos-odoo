# © 2023 Lucia Pinero Consultoría Informática (<http://www.luciapinero.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Helpdesk mgmt Maintenance",
    "summary": """
        Helpdesk mgmt Maintenance
    """,
    "author": "Luciana Pinheiro",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Inventory/Maintenance/Helpdesk",
    "website": "https://github.com/LucPinheiro/FCT-project",
    "depends": [
        "maintenance",
        "helpdesk_mgmt",
        "project", 
        "hr_maintenance",
    ],
    "data": [
        "data/maintenance_demo.xml",
        "security/ir.model.access.csv",
        "report/equipment_traceability_template.xml",
        "report/ticket_traceability_template.xml",
        "report/request_traceability_template.xml",
        "report/equipment_wizard_report.xml",
        "views/menus.xml",     
        "views/maintenance_equipment_views.xml",
        "views/project_project_line.xml",
        "views/maintenance_equipment_brand.xml",
        "views/maintenance_equipment_status.xml",
        "views/maintenance_request.xml",
        "views/helpdesk_mgmt_views.xml",
        "views/helpdesk_ticket_line_views.xml",
        "views/project_views.xml",

    ],
    'installable': True,
}
