# -*- coding: utf-8 -*-
import base64
import binascii
import io
import zipfile

from odoo import _, fields, models
from odoo.exceptions import UserError


class ImportProductDescriptionWizard(models.TransientModel):
    _name = "ecommerce.product.description.translation.import.wizard"
    _description = "Importar traducciones HTML de productos"

    file = fields.Binary(string="Archivo Excel (.xlsx)", required=True)
    filename = fields.Char(string="Nombre del archivo")

    def action_import(self):
        self.ensure_one()
        if not self.filename or not self.filename.lower().endswith(".xlsx"):
            raise UserError(_("Selecciona un archivo .xlsx válido."))
        try:
            import openpyxl
            data = base64.b64decode(self.file, validate=True)
            workbook = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
            sheet = workbook.active
            headers = [str(c.value).strip() if c.value is not None else "" for c in sheet[1]]
            required = {"id", "lang"}
            missing = required - set(headers)
            if missing:
                raise UserError(_("Faltan columnas obligatorias: %s") % ", ".join(sorted(missing)))
            content_fields = {"short_description_product", "full_description_product"}
            if not content_fields.intersection(headers):
                raise UserError(_("El Excel debe incluir al menos una columna de contenido: %s") % ", ".join(sorted(content_fields)))
            if len(set(headers)) != len(headers):
                raise UserError(_("Hay encabezados duplicados en el Excel."))

            products = self.env["product.template"]
            active_langs = set(self.env["res.lang"].search([("active", "=", True)]).mapped("code"))
            seen = set()
            rows = []
            errors = []
            for row_num, values in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                row = dict(zip(headers, values))
                if not any(value is not None and value != "" for value in row.values()):
                    continue
                raw_id = row.get("id")
                lang = str(row.get("lang") or "").strip()
                try:
                    if isinstance(raw_id, bool) or raw_id is None or str(raw_id).strip() == "" or float(raw_id) != int(float(raw_id)) or int(float(raw_id)) <= 0:
                        raise ValueError()
                    product_id = int(float(raw_id))
                except (TypeError, ValueError, OverflowError):
                    errors.append(_("Fila %s: ID de producto inválido.") % row_num)
                    continue
                if lang not in active_langs:
                    errors.append(_("Fila %s: idioma no activo o desconocido: %s") % (row_num, lang))
                    continue
                key = (product_id, lang)
                if key in seen:
                    errors.append(_("Fila %s: combinación ID/idioma duplicada: %s / %s") % (row_num, product_id, lang))
                    continue
                seen.add(key)
                product = products.browse(product_id)
                if not product.exists():
                    errors.append(_("Fila %s: no existe producto con ID %s.") % (row_num, product_id))
                    continue
                values_to_write = {}
                for field in content_fields.intersection(headers):
                    value = row.get(field)
                    if value is None or value == "":
                        continue  # Vacío significa no modificar el valor existente.
                    if not isinstance(value, str):
                        errors.append(_("Fila %s: el campo %s debe contener texto.") % (row_num, field))
                        continue
                    values_to_write[field] = value
                if values_to_write:
                    rows.append((product, lang, values_to_write))
            if errors:
                raise UserError(_("Corrige el archivo antes de importar:\n%s") % "\n".join(errors[:80]))
            if not rows:
                raise UserError(_("No hay contenido para importar. Las celdas vacías no modifican campos."))
            now = fields.Datetime.now()
            imported_fields = {}
            for product, lang, values_to_write in rows:
                # La traducción se escribe con el ORM de Odoo, sin SQL directo.
                product.with_context(lang=lang).write(values_to_write)
                imported_fields.setdefault(product.id, set()).update(values_to_write)
            for product_id, field_names in imported_fields.items():
                products.browse(product_id).write({
                    "html_translation_state": "translated" if len(field_names) == 2 else "partial",
                    "html_translation_import_date": now,
                    "html_translation_user_id": self.env.user.id,
                    "html_pending_preparation": False,
                })
            workbook.close()
        except UserError:
            raise
        except (OSError, ValueError, binascii.Error, zipfile.BadZipFile) as exc:
            raise UserError(_("No se pudo abrir el Excel: %s") % str(exc)) from exc
        return {
            "type": "ir.actions.client", "tag": "display_notification",
            "params": {"title": _("Importación completada"),
                       "message": _("Se han procesado %s filas de traducción.") % len(rows),
                       "type": "success", "sticky": False,
                       "next": {"type": "ir.actions.act_window_close"}},
        }
