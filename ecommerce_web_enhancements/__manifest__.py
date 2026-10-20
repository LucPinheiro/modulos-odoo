# -*- coding: utf-8 -*-
{
    "name": "E-commerce Web Enhancements",
    "summary": "Mejoras visuales y de contenido para la tienda online de Odoo 19.",
    "version": "19.0.2.0.0",
    "category": "Website/Website",
    "author": "Kodexia Solutions",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": ["base", "web", "website", "website_sale"],
    "data": [
        "views/website_sale_template.xml",
        "views/product_template.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/ecommerce_web_enhancements/static/src/scss/website_sale_style.scss",
        ],
    },
}
