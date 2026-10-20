# -*- coding: utf-8 -*-
{
    "name": "E-commerce Product Description Translations",
    "summary": "Traducción de descripciones cortas y largas de productos del e-commerce.",
    "version": "19.0.1.0.0",
    "category": "Website/Website",
    "author": "Kodexia Solutions",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "external_dependencies": {"python": ["openpyxl"]},
    "depends": ["ecommerce_web_enhancements"],
    "data": [
        "security/ir.model.access.csv",
        "views/import_product_description_wizard_views.xml",
        "views/product_template_views.xml",
    ],
}
