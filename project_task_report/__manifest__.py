#)License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Projet Task Report",
    "summary": """ Add filters in project and task view """,
    "author": "i2T",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Project",
    "website": "",
    'depends': ["project", "i2t_task_management"],
    "data": [        
        "views/project_project_views.xml",
        "views/project_task_views.xml",
        "report/project_report_views.xml",
    ],
    'installable': True,
}
