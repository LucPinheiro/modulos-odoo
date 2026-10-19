# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Task Billable Management",
    "summary": """
      Restrict user to not change task status to completed or
        rejected and only assign hours to tasks whose status is
        “Doing” and if they are billable.
    """,
    "author": "i2T",
    "license": "LGPL-3",
    "version": "15.0.1.0.0",
    "category": "Project",
    "website": "",
    'depends': ["project", "hr_timesheet", "sale_timesheet"],
    "data": [        
        "views/project_task_views.xml",
        "views/account_analytic_line_views.xml",
    ],
    'installable': True,
}
