# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    short_description_product = fields.Html(
        string="Descripción corta web",
        translate=True,
        copy=False,
        help="Se muestra en la ficha del producto junto al precio.",
    )

    full_description_product = fields.Html(
        string="Descripción larga web (adicional)",
        translate=True,
        copy=False,
        help="Campo adicional de contenido web; la pestaña principal usa la descripción web estándar de Odoo.",
    )

    @api.model
    def _get_accessories_product_filter(self):
        record = self.env.ref(
            "website_sale.dynamic_filter_cross_selling_accessories",
            raise_if_not_found=False,
        )
        return record.id if record else False
