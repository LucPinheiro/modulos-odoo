import base64
import json
import logging
import re
import unicodedata
from datetime import timedelta
from urllib.parse import urlencode, urlparse

import requests

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.float_utils import float_compare


_logger = logging.getLogger(__name__)

OCR_PROTECTED_FIELDS = {
    "vendor_bill_ocr_state",
    "vendor_bill_ocr_provider",
    "vendor_bill_ocr_confidence",
    "vendor_bill_ocr_vendor_name",
    "vendor_bill_ocr_vendor_vat",
    "vendor_bill_ocr_customer_vat",
    "vendor_bill_ocr_vendor_address",
    "vendor_bill_ocr_subtotal",
    "vendor_bill_ocr_tax_total",
    "vendor_bill_ocr_invoice_total",
    "vendor_bill_ocr_tax_rates",
    "vendor_bill_ocr_detected_iban",
    "vendor_bill_ocr_payment_term",
    "vendor_bill_ocr_warning",
    "vendor_bill_ocr_error",
    "vendor_bill_ocr_attempts",
    "vendor_bill_ocr_next_retry",
    "vendor_bill_ocr_submitted_at",
    "vendor_bill_ocr_processed_at",
    "vendor_bill_ocr_document_hash",
    "vendor_bill_ocr_operation_url",
    "vendor_bill_ocr_raw_response",
    "vendor_bill_ocr_source_attachment_id",
    "vendor_bill_ocr_source_pages",
    "vendor_bill_ocr_processed_pages",
    "vendor_bill_ocr_duplicate_id",
    "vendor_bill_ocr_usage_log_id",
    "vendor_bill_ocr_reviewed_by_id",
    "vendor_bill_ocr_reviewed_at",
}


class AccountMove(models.Model):
    _inherit = "account.move"

    vendor_bill_ocr_state = fields.Selection(
        [
            ("not_used", "Sin OCR"),
            ("pending", "Pendiente"),
            ("processing", "Procesando"),
            ("review", "Revisar"),
            ("done", "Revisado"),
            ("error", "Error"),
        ],
        string="Estado OCR",
        default="not_used",
        required=True,
        copy=False,
        index=True,
        tracking=True,
    )
    vendor_bill_ocr_provider = fields.Selection(
        [("azure", "Azure Document Intelligence")], copy=False
    )
    vendor_bill_ocr_confidence = fields.Float(
        string="Confianza OCR (%)", digits=(5, 2), copy=False
    )
    vendor_bill_ocr_vendor_name = fields.Char(string="Proveedor detectado", copy=False)
    vendor_bill_ocr_vendor_vat = fields.Char(string="NIF/VAT detectado", copy=False)
    vendor_bill_ocr_customer_vat = fields.Char(
        string="NIF/VAT del cliente detectado", copy=False
    )
    vendor_bill_ocr_vendor_address = fields.Char(
        string="Dirección del proveedor detectada", copy=False
    )
    vendor_bill_ocr_subtotal = fields.Monetary(
        string="Base detectada", currency_field="currency_id", copy=False
    )
    vendor_bill_ocr_tax_total = fields.Monetary(
        string="Impuestos detectados", currency_field="currency_id", copy=False
    )
    vendor_bill_ocr_invoice_total = fields.Monetary(
        string="Total detectado", currency_field="currency_id", copy=False
    )
    vendor_bill_ocr_tax_rates = fields.Char(
        string="Tipos de impuesto detectados", copy=False
    )
    vendor_bill_ocr_detected_iban = fields.Char(string="IBAN detectado", copy=False)
    vendor_bill_ocr_payment_term = fields.Char(
        string="Condición de pago detectada", copy=False
    )
    vendor_bill_ocr_warning = fields.Text(string="Avisos OCR", copy=False)
    vendor_bill_ocr_error = fields.Text(string="Error OCR", copy=False)
    vendor_bill_ocr_attempts = fields.Integer(
        string="Intentos OCR", default=0, copy=False
    )
    vendor_bill_ocr_next_retry = fields.Datetime(
        string="Próximo intento OCR", copy=False
    )
    vendor_bill_ocr_submitted_at = fields.Datetime(string="Enviado a Azure", copy=False)
    vendor_bill_ocr_processed_at = fields.Datetime(string="Procesado el", copy=False)
    vendor_bill_ocr_document_hash = fields.Char(
        string="Huella del documento", index=True, copy=False, groups="base.group_system"
    )
    vendor_bill_ocr_operation_url = fields.Char(
        string="URL de operación OCR", copy=False, groups="base.group_system"
    )
    vendor_bill_ocr_raw_response = fields.Text(
        string="Respuesta OCR", copy=False, groups="base.group_system"
    )
    vendor_bill_ocr_source_attachment_id = fields.Many2one(
        "ir.attachment", string="Documento original", copy=False, ondelete="set null"
    )
    vendor_bill_ocr_source_pages = fields.Integer(
        string="Páginas del archivo", copy=False
    )
    vendor_bill_ocr_processed_pages = fields.Integer(
        string="Páginas procesadas", copy=False
    )
    vendor_bill_ocr_duplicate_id = fields.Many2one(
        "account.move", string="Posible duplicado", copy=False, ondelete="set null"
    )
    vendor_bill_ocr_project_id = fields.Many2one(
        "project.project",
        string="Proyecto OCR",
        copy=False,
        check_company=True,
        help="Proyecto seleccionado en el wizard para cargarlo en las líneas OCR.",
    )
    vendor_bill_ocr_usage_log_id = fields.Many2one(
        "snk.vendor.bill.ocr.usage.log",
        string="Registro de consumo",
        copy=False,
        ondelete="set null",
        groups="base.group_system",
    )
    vendor_bill_ocr_review_note = fields.Text(
        string="Nota de revisión",
        copy=False,
        help="Obligatoria para aceptar una factura marcada como posible duplicado.",
    )
    vendor_bill_ocr_reviewed_by_id = fields.Many2one(
        "res.users", string="Revisado por", copy=False, ondelete="set null"
    )
    vendor_bill_ocr_reviewed_at = fields.Datetime(string="Revisado el", copy=False)

    _sql_constraints = [
        (
            "vendor_bill_ocr_company_hash_unique",
            "unique(company_id, vendor_bill_ocr_document_hash)",
            "Este documento ya se utilizó en otra factura de la compañía.",
        )
    ]

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not self.env.user.has_group("account.group_account_manager"):
            if any(OCR_PROTECTED_FIELDS.intersection(values) for values in vals_list):
                raise AccessError(_("No puede establecer directamente los campos técnicos OCR."))
        return super().create(vals_list)

    def write(self, values):
        if (
            OCR_PROTECTED_FIELDS.intersection(values)
            and not self.env.su
            and not self.env.user.has_group("account.group_account_manager")
        ):
            raise AccessError(_("No puede modificar directamente los campos técnicos OCR."))
        return super().write(values)

    def _vendor_bill_ocr_check_user_can_operate(self):
        is_invoice_user = self.env.user.has_group("account.group_account_invoice")
        is_ocr_user = self.env.user.has_group("snk_vendor_bill_ocr.group_vendor_bill_ocr_user")
        if not (is_invoice_user or is_ocr_user):
            raise AccessError(_("No tiene permiso para procesar facturas de proveedor."))
        for move in self:
            if move.company_id not in self.env.user.company_ids:
                raise AccessError(_("No tiene acceso a la compañía de la factura."))
            if move.move_type != "in_invoice" or move.state != "draft":
                raise UserError(_("Solo se procesan facturas de proveedor en borrador."))
            if is_ocr_user and not is_invoice_user and move.create_uid != self.env.user:
                raise AccessError(
                    _("Solo puede operar facturas de compra cargadas por usted.")
                )

    def action_vendor_bill_ocr_process_now(self):
        self._vendor_bill_ocr_check_user_can_operate()
        for move in self:
            if move.vendor_bill_ocr_state not in ("pending", "processing"):
                raise UserError(_("La factura no está pendiente de procesamiento OCR."))
            move.sudo()._vendor_bill_ocr_process_step()
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_vendor_bill_ocr_retry(self):
        self._vendor_bill_ocr_check_user_can_operate()
        self.sudo().write(
            {
                "vendor_bill_ocr_state": "pending",
                "vendor_bill_ocr_error": False,
                "vendor_bill_ocr_warning": False,
                "vendor_bill_ocr_attempts": 0,
                "vendor_bill_ocr_next_retry": fields.Datetime.now(),
                "vendor_bill_ocr_operation_url": False,
                "vendor_bill_ocr_usage_log_id": False,
            }
        )
        return self.action_vendor_bill_ocr_process_now()

    def action_vendor_bill_ocr_mark_reviewed(self):
        self._vendor_bill_ocr_check_user_can_operate()
        for move in self:
            if move.vendor_bill_ocr_state != "review":
                raise UserError(_("La factura no está pendiente de revisión."))
            missing = []
            if not move.partner_id:
                missing.append(_("proveedor"))
            if not move.invoice_date:
                missing.append(_("fecha de factura"))
            if not (move.ref or "").strip():
                missing.append(_("referencia del proveedor"))
            commercial_lines = move.invoice_line_ids.filtered(
                lambda line: line.display_type not in ("line_section", "line_note")
            )
            if not commercial_lines:
                missing.append(_("líneas de factura"))
            if commercial_lines.filtered(lambda line: not line.account_id):
                missing.append(_("cuenta contable en todas las líneas"))
            if float_compare(
                move.amount_total, 0.0, precision_rounding=move.currency_id.rounding
            ) <= 0:
                missing.append(_("importe total positivo"))
            if not move.vendor_bill_ocr_source_attachment_id:
                missing.append(_("documento original"))
            if move.vendor_bill_ocr_duplicate_id and not (
                move.vendor_bill_ocr_review_note or ""
            ).strip():
                missing.append(_("nota justificativa para el posible duplicado"))
            if missing:
                raise UserError(
                    _("Complete estos datos antes de validar la revisión: %s")
                    % ", ".join(missing)
                )
            move.sudo().write(
                {
                    "vendor_bill_ocr_state": "done",
                    "vendor_bill_ocr_error": False,
                    "vendor_bill_ocr_reviewed_by_id": self.env.user.id,
                    "vendor_bill_ocr_reviewed_at": fields.Datetime.now(),
                    "to_check": False,
                }
            )
            move.message_post(
                body=_("%s confirmó la revisión de los datos OCR.")
                % self.env.user.display_name
            )
        return {"type": "ir.actions.client", "tag": "reload"}

    def action_post(self):
        blocked = self.filtered(
            lambda move: move.move_type == "in_invoice"
            and move.vendor_bill_ocr_state in ("pending", "processing", "review", "error")
        )
        if blocked:
            raise UserError(
                _(
                    "No puede contabilizar facturas cuyo OCR esté pendiente, "
                    "con error o sin revisar: %s"
                )
                % ", ".join(blocked.mapped("display_name")[:5])
            )
        return super().action_post()

    @api.model
    def _cron_process_vendor_bill_ocr(self):
        now = fields.Datetime.now()
        companies = self.env["res.company"].sudo().search(
            [("vendor_bill_ocr_enabled", "=", True)]
        )
        for company in companies:
            moves = (
                self.sudo()
                .with_company(company)
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("move_type", "=", "in_invoice"),
                        ("state", "=", "draft"),
                        ("vendor_bill_ocr_state", "in", ("pending", "processing")),
                        "|",
                        ("vendor_bill_ocr_next_retry", "=", False),
                        ("vendor_bill_ocr_next_retry", "<=", now),
                    ],
                    order="vendor_bill_ocr_next_retry, id",
                    limit=company.vendor_bill_ocr_batch_size,
                )
            )
            for move in moves:
                try:
                    with self.env.cr.savepoint():
                        move._vendor_bill_ocr_process_step()
                except Exception:  # pragma: no cover - final cron protection
                    _logger.exception("Unexpected vendor bill OCR error for %s", move.id)
                    with self.env.cr.savepoint():
                        move._vendor_bill_ocr_register_error(
                            _("Error interno inesperado durante el OCR."), transient=True
                        )

    def _vendor_bill_ocr_process_step(self):
        self.ensure_one()
        company = self.company_id.sudo()
        if self.move_type != "in_invoice" or self.state != "draft":
            self._vendor_bill_ocr_register_error(
                _("La factura dejó de ser un borrador de proveedor."), False
            )
            return
        if not company.vendor_bill_ocr_enabled:
            self._vendor_bill_ocr_register_error(
                _("El OCR está desactivado para esta compañía."), False
            )
            return
        try:
            company._vendor_bill_ocr_validate_azure_url(
                company.vendor_bill_ocr_azure_endpoint or ""
            )
        except ValidationError as error:
            self._vendor_bill_ocr_register_error(str(error), False)
            return
        if not company._vendor_bill_ocr_get_api_key():
            self._vendor_bill_ocr_register_error(
                _("No hay una clave de Azure configurada."), False
            )
            return
        if self.vendor_bill_ocr_state == "pending":
            self._vendor_bill_ocr_submit_azure()
        elif self.vendor_bill_ocr_state == "processing":
            self._vendor_bill_ocr_poll_azure()

    def _vendor_bill_ocr_submit_azure(self):
        self.ensure_one()
        company = self.company_id.sudo()
        attachment = self.vendor_bill_ocr_source_attachment_id.sudo()
        if not attachment or not attachment.datas:
            self._vendor_bill_ocr_register_error(
                _("No se encuentra el documento original adjunto."), False
            )
            return
        try:
            payload = base64.b64decode(attachment.datas, validate=True)
        except (ValueError, TypeError):
            self._vendor_bill_ocr_register_error(_("El adjunto está dañado."), False)
            return

        try:
            usage_log = company._vendor_bill_ocr_check_and_log_quota(self)
        except UserError as error:
            self._vendor_bill_ocr_register_error(str(error), False)
            return
        self.sudo().write({"vendor_bill_ocr_usage_log_id": usage_log.id})

        endpoint = company.vendor_bill_ocr_azure_endpoint.rstrip("/")
        query = urlencode(
            {
                "api-version": company.vendor_bill_ocr_azure_api_version,
                "pages": "1-%s" % company.vendor_bill_ocr_max_pages,
            }
        )
        url = (
            endpoint
            + "/documentintelligence/documentModels/prebuilt-invoice:analyze?"
            + query
        )
        headers = {
            "Ocp-Apim-Subscription-Key": company._vendor_bill_ocr_get_api_key(),
            "Content-Type": attachment.mimetype or "application/octet-stream",
        }
        try:
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                timeout=(5, 60),
                allow_redirects=False,
            )
        except (requests.Timeout, requests.ConnectionError) as error:
            usage_log.sudo().write({"status": "failed", "error": str(error)[:250]})
            self._vendor_bill_ocr_register_error(
                _("No se pudo conectar con Azure: %s") % str(error)[:200], True
            )
            return
        except requests.RequestException as error:
            usage_log.sudo().write({"status": "failed", "error": str(error)[:250]})
            self._vendor_bill_ocr_register_error(
                _("Error de comunicación con Azure: %s") % str(error)[:200], True
            )
            return

        usage_log.sudo().write({"http_status": response.status_code})
        if response.status_code == 200:
            usage_log.sudo().write({"status": "accepted"})
            try:
                result = response.json()
            except ValueError:
                usage_log.sudo().write({"status": "failed", "error": "Invalid JSON"})
                self._vendor_bill_ocr_register_error(
                    _("Azure devolvió una respuesta no válida."), False
                )
                return
            self.sudo().write({"vendor_bill_ocr_submitted_at": fields.Datetime.now()})
            self._vendor_bill_ocr_finish_azure_result(result, usage_log)
            return
        if response.status_code != 202:
            self._vendor_bill_ocr_handle_http_error(response, "pending", usage_log)
            return

        operation_url = response.headers.get("Operation-Location")
        if not operation_url:
            usage_log.sudo().write(
                {"status": "failed", "error": "Missing Operation-Location"}
            )
            self._vendor_bill_ocr_register_error(
                _("Azure no devolvió la URL de seguimiento de la operación."), False
            )
            return
        try:
            company._vendor_bill_ocr_validate_azure_url(operation_url, operation_url=True)
        except ValidationError as error:
            usage_log.sudo().write({"status": "failed", "error": str(error)[:250]})
            self._vendor_bill_ocr_register_error(str(error), False)
            return
        operation_id = urlparse(operation_url).path.rstrip("/").split("/")[-1]
        usage_log.sudo().write(
            {"status": "accepted", "operation_id": operation_id[:255]}
        )
        self.sudo().write(
            {
                "vendor_bill_ocr_state": "processing",
                "vendor_bill_ocr_provider": "azure",
                "vendor_bill_ocr_operation_url": operation_url,
                "vendor_bill_ocr_error": False,
                "vendor_bill_ocr_attempts": 0,
                "vendor_bill_ocr_submitted_at": fields.Datetime.now(),
                "vendor_bill_ocr_next_retry": fields.Datetime.now()
                + timedelta(minutes=1),
            }
        )

    def _vendor_bill_ocr_poll_azure(self):
        self.ensure_one()
        company = self.company_id.sudo()
        if not self.vendor_bill_ocr_operation_url:
            self._vendor_bill_ocr_register_error(
                _("Falta la URL de seguimiento de Azure."), False
            )
            return
        try:
            company._vendor_bill_ocr_validate_azure_url(
                self.vendor_bill_ocr_operation_url, operation_url=True
            )
        except ValidationError as error:
            self._vendor_bill_ocr_register_error(str(error), False)
            return
        try:
            response = requests.get(
                self.vendor_bill_ocr_operation_url,
                headers={"Ocp-Apim-Subscription-Key": company._vendor_bill_ocr_get_api_key()},
                timeout=(5, 60),
                allow_redirects=False,
            )
        except (requests.Timeout, requests.ConnectionError) as error:
            self._vendor_bill_ocr_register_error(
                _("No se pudo consultar Azure: %s") % str(error)[:200], True
            )
            return
        except requests.RequestException as error:
            self._vendor_bill_ocr_register_error(
                _("Error consultando Azure: %s") % str(error)[:200], True
            )
            return
        if response.status_code != 200:
            self._vendor_bill_ocr_handle_http_error(response, "processing")
            return
        try:
            result = response.json()
        except ValueError:
            self._vendor_bill_ocr_register_error(
                _("Azure devolvió una respuesta no válida."), True
            )
            return
        status = (result.get("status") or "").lower()
        if status in ("running", "notstarted"):
            attempts = self.vendor_bill_ocr_attempts + 1
            if attempts >= company.vendor_bill_ocr_max_attempts:
                self._vendor_bill_ocr_register_error(
                    _("Azure no terminó dentro del número máximo de consultas."), False
                )
                return
            self.sudo().write(
                {
                    "vendor_bill_ocr_attempts": attempts,
                    "vendor_bill_ocr_next_retry": fields.Datetime.now()
                    + timedelta(minutes=1),
                    "vendor_bill_ocr_error": False,
                }
            )
            return
        if status == "failed":
            error = result.get("error") or {}
            message = error.get("message") or _("Azure no pudo analizar la factura.")
            if self.vendor_bill_ocr_usage_log_id:
                self.vendor_bill_ocr_usage_log_id.sudo().write(
                    {"status": "failed", "error": str(message)[:250]}
                )
            self._vendor_bill_ocr_register_error(str(message)[:500], False)
            return
        if status != "succeeded":
            self._vendor_bill_ocr_register_error(
                _("Estado desconocido devuelto por Azure: %s") % status, True
            )
            return
        self._vendor_bill_ocr_finish_azure_result(
            result, self.vendor_bill_ocr_usage_log_id
        )

    def _vendor_bill_ocr_handle_http_error(self, response, retry_state, usage_log=None):
        self.ensure_one()
        transient = response.status_code == 429 or response.status_code >= 500
        message = _("Azure devolvió el error HTTP %s.") % response.status_code
        try:
            detail = response.json().get("error", {}).get("message")
            if detail:
                message += " " + str(detail)[:300]
        except (ValueError, AttributeError):
            pass
        log = usage_log or self.vendor_bill_ocr_usage_log_id
        if log:
            log.sudo().write(
                {
                    "status": "failed",
                    "http_status": response.status_code,
                    "error": message[:250],
                }
            )
        if transient:
            self.sudo().write({"vendor_bill_ocr_state": retry_state})
        self._vendor_bill_ocr_register_error(message, transient)

    def _vendor_bill_ocr_register_error(self, message, transient):
        self.ensure_one()
        attempts = self.vendor_bill_ocr_attempts + 1
        max_attempts = self.company_id.vendor_bill_ocr_max_attempts or 1
        if transient and attempts < max_attempts:
            delay = min(2 ** attempts, 60)
            values = {
                "vendor_bill_ocr_attempts": attempts,
                "vendor_bill_ocr_error": message,
                "vendor_bill_ocr_next_retry": fields.Datetime.now()
                + timedelta(minutes=delay),
            }
        else:
            values = {
                "vendor_bill_ocr_state": "error",
                "vendor_bill_ocr_attempts": attempts,
                "vendor_bill_ocr_error": message,
                "vendor_bill_ocr_next_retry": False,
            }
        self.sudo().write(values)

    def _vendor_bill_ocr_finish_azure_result(self, response, usage_log=None):
        self.ensure_one()
        try:
            parsed = self._vendor_bill_ocr_parse_azure_result(response)
        except ValidationError as error:
            if usage_log:
                usage_log.sudo().write({"status": "failed", "error": str(error)[:250]})
            self._vendor_bill_ocr_register_error(str(error), False)
            return
        self._vendor_bill_ocr_apply_result(parsed, response, usage_log)

    @api.model
    def _vendor_bill_ocr_field_value(self, document_fields, *names):
        field_data = {}
        for name in names:
            if document_fields.get(name):
                field_data = document_fields[name]
                break
        if not field_data:
            return False, 0.0, {}
        value = False
        for key in (
            "valueString",
            "valueDate",
            "valueTime",
            "valueNumber",
            "valueInteger",
            "valuePhoneNumber",
        ):
            if key in field_data:
                value = field_data[key]
                break
        currency = field_data.get("valueCurrency") or {}
        if currency:
            value = currency.get("amount")
        address = field_data.get("valueAddress") or {}
        if address and value is False:
            value = field_data.get("content") or ", ".join(
                str(part) for part in address.values() if part
            )
        if value is False:
            value = field_data.get("content")
        return value, float(field_data.get("confidence") or 0.0), field_data

    @api.model
    def _vendor_bill_ocr_object_fields(self, array_item):
        value_object = (array_item or {}).get("valueObject") or {}
        return value_object.get("fields") or value_object

    @api.model
    def _vendor_bill_ocr_parse_azure_result(self, response):
        analyze_result = response.get("analyzeResult") or {}
        documents = analyze_result.get("documents") or []
        if not documents:
            raise ValidationError(_("Azure no encontró ninguna factura en el archivo."))
        document = documents[0]
        document_fields = document.get("fields") or {}

        vendor_name, vendor_confidence, _ = self._vendor_bill_ocr_field_value(
            document_fields, "VendorName"
        )
        vendor_vat, vendor_vat_confidence, _ = self._vendor_bill_ocr_field_value(
            document_fields, "VendorTaxId"
        )
        customer_vat, _, _ = self._vendor_bill_ocr_field_value(
            document_fields, "CustomerTaxId"
        )
        vendor_address, _, _ = self._vendor_bill_ocr_field_value(
            document_fields, "VendorAddress"
        )
        invoice_id, reference_confidence, _ = self._vendor_bill_ocr_field_value(
            document_fields, "InvoiceId"
        )
        invoice_date, date_confidence, _ = self._vendor_bill_ocr_field_value(
            document_fields, "InvoiceDate"
        )
        due_date, _, _ = self._vendor_bill_ocr_field_value(document_fields, "DueDate")
        purchase_order, _, _ = self._vendor_bill_ocr_field_value(
            document_fields, "PurchaseOrder"
        )
        payment_term, _, _ = self._vendor_bill_ocr_field_value(
            document_fields, "PaymentTerm"
        )
        subtotal, _, _ = self._vendor_bill_ocr_field_value(
            document_fields, "SubTotal", "Subtotal"
        )
        tax_total, _, _ = self._vendor_bill_ocr_field_value(
            document_fields, "TotalTax"
        )
        invoice_total, total_confidence, total_data = self._vendor_bill_ocr_field_value(
            document_fields, "InvoiceTotal", "AmountDue"
        )

        raw_content = analyze_result.get("content") or ""
        vendor_vat = vendor_vat or self._vendor_bill_ocr_extract_labeled_tax_id(
            raw_content, ("NIF", "CIF", "VAT", "VAT ID", "TAX ID")
        )
        iban = self._vendor_bill_ocr_extract_iban(document_fields, raw_content)
        tax_details = self._vendor_bill_ocr_parse_tax_details(document_fields)
        items = self._vendor_bill_ocr_parse_items(document_fields)
        currency_data = total_data.get("valueCurrency") or {}
        currency_code = currency_data.get("currencyCode")
        confidences = [
            value
            for value in (
                vendor_confidence,
                vendor_vat_confidence,
                reference_confidence,
                date_confidence,
                total_confidence,
                float(document.get("confidence") or 0.0),
            )
            if value
        ]
        return {
            "document_count": len(documents),
            "page_count": len(analyze_result.get("pages") or []),
            "vendor_name": str(vendor_name).strip()[:255] if vendor_name else False,
            "vendor_vat": str(vendor_vat).strip().upper()[:64] if vendor_vat else False,
            "customer_vat": str(customer_vat).strip().upper()[:64]
            if customer_vat
            else False,
            "vendor_address": str(vendor_address).strip()[:500]
            if vendor_address
            else False,
            "invoice_id": str(invoice_id).strip()[:255] if invoice_id else False,
            "invoice_date": invoice_date or False,
            "due_date": due_date or False,
            "purchase_order": str(purchase_order).strip()[:255]
            if purchase_order
            else False,
            "payment_term": str(payment_term).strip()[:255] if payment_term else False,
            "subtotal": self._vendor_bill_ocr_to_float(subtotal),
            "tax_total": self._vendor_bill_ocr_to_float(tax_total),
            "invoice_total": self._vendor_bill_ocr_to_float(invoice_total),
            "currency": currency_code or False,
            "iban": iban,
            "tax_details": tax_details,
            "items": items,
            "confidence": min(confidences) if confidences else 0.0,
        }

    @api.model
    def _vendor_bill_ocr_parse_items(self, document_fields):
        items_field = document_fields.get("Items") or {}
        items = []
        for array_item in items_field.get("valueArray") or []:
            item_fields = self._vendor_bill_ocr_object_fields(array_item)
            description, desc_confidence, _ = self._vendor_bill_ocr_field_value(
                item_fields, "Description"
            )
            product_code, code_confidence, _ = self._vendor_bill_ocr_field_value(
                item_fields, "ProductCode"
            )
            quantity, quantity_confidence, _ = self._vendor_bill_ocr_field_value(
                item_fields, "Quantity"
            )
            unit, _, _ = self._vendor_bill_ocr_field_value(item_fields, "Unit")
            unit_price, price_confidence, _ = self._vendor_bill_ocr_field_value(
                item_fields, "UnitPrice"
            )
            amount, amount_confidence, _ = self._vendor_bill_ocr_field_value(
                item_fields, "Amount"
            )
            tax, _, _ = self._vendor_bill_ocr_field_value(item_fields, "Tax")
            tax_rate, _, tax_rate_data = self._vendor_bill_ocr_field_value(
                item_fields, "TaxRate"
            )
            rate = self._vendor_bill_ocr_percent_to_float(
                tax_rate, tax_rate_data.get("content")
            )
            confidences = [
                value
                for value in (
                    desc_confidence,
                    code_confidence,
                    quantity_confidence,
                    price_confidence,
                    amount_confidence,
                )
                if value
            ]
            items.append(
                {
                    "description": str(description).strip()[:1000]
                    if description
                    else False,
                    "product_code": str(product_code).strip()[:255]
                    if product_code
                    else False,
                    "quantity": self._vendor_bill_ocr_to_float(quantity),
                    "unit": str(unit).strip()[:64] if unit else False,
                    "unit_price": self._vendor_bill_ocr_to_float(unit_price),
                    "amount": self._vendor_bill_ocr_to_float(amount),
                    "tax": self._vendor_bill_ocr_to_float(tax),
                    "tax_rate": rate,
                    "confidence": min(confidences) if confidences else 0.0,
                }
            )
        return items

    @api.model
    def _vendor_bill_ocr_parse_tax_details(self, document_fields):
        details_field = document_fields.get("TaxDetails") or {}
        result = []
        for array_item in details_field.get("valueArray") or []:
            detail_fields = self._vendor_bill_ocr_object_fields(array_item)
            amount, _, _ = self._vendor_bill_ocr_field_value(detail_fields, "Amount")
            rate, _, rate_data = self._vendor_bill_ocr_field_value(
                detail_fields, "Rate", "TaxRate"
            )
            parsed_rate = self._vendor_bill_ocr_percent_to_float(
                rate, rate_data.get("content")
            )
            result.append(
                {
                    "amount": self._vendor_bill_ocr_to_float(amount),
                    "rate": parsed_rate,
                }
            )
        return result

    @api.model
    def _vendor_bill_ocr_extract_iban(self, document_fields, raw_content):
        payment_details = document_fields.get("PaymentDetails") or {}
        for array_item in payment_details.get("valueArray") or []:
            detail_fields = self._vendor_bill_ocr_object_fields(array_item)
            iban, _, _ = self._vendor_bill_ocr_field_value(detail_fields, "IBAN")
            normalized = self._vendor_bill_ocr_normalize_iban(iban)
            if normalized:
                return normalized
        match = re.search(
            r"\b[A-Z]{2}\s*\d{2}(?:[\s.-]*[A-Z0-9]){11,30}\b",
            raw_content or "",
            re.IGNORECASE,
        )
        return self._vendor_bill_ocr_normalize_iban(match.group(0)) if match else False

    @api.model
    def _vendor_bill_ocr_extract_labeled_tax_id(self, raw_content, labels):
        label_pattern = "|".join(re.escape(label) for label in labels)
        match = re.search(
            r"\b(?:%s)\s*[:\-]?\s*([A-Z0-9][A-Z0-9 .\-]{6,20})" % label_pattern,
            raw_content or "",
            re.IGNORECASE,
        )
        return match.group(1).strip() if match else False

    @api.model
    def _vendor_bill_ocr_percent_to_float(self, value, content=None):
        if isinstance(value, (int, float)):
            # Azure normally returns a percentage (21), but some payloads use a
            # fraction (0.21).  Exactly 1 is kept as 1% because multiplying it
            # would turn a perfectly valid reduced rate into 100%.
            return float(value * 100 if 0 < value < 1 else value)
        candidate = str(value or content or "")
        match = re.search(r"(-?\d{1,3}(?:[.,]\d+)?)", candidate)
        return float(match.group(1).replace(",", ".")) if match else None

    @api.model
    def _vendor_bill_ocr_to_float(self, value):
        # Do not lose numeric zero: it is significant for tax-exempt invoices.
        if value is False or value is None or value == "":
            return False
        if isinstance(value, (int, float)):
            return float(value)
        normalized = re.sub(r"[^0-9,.-]", "", str(value))
        if normalized.count(",") == 1 and normalized.count(".") >= 1:
            normalized = normalized.replace(".", "").replace(",", ".")
        elif normalized.count(",") == 1:
            normalized = normalized.replace(",", ".")
        try:
            return float(normalized)
        except ValueError:
            return False

    def _vendor_bill_ocr_apply_result(self, parsed, raw_response=None, usage_log=None):
        self.ensure_one()
        if self.move_type != "in_invoice" or self.state != "draft":
            self._vendor_bill_ocr_register_error(
                _("La factura ya no es un borrador de proveedor."), False
            )
            return
        company = self.company_id.sudo()
        warnings = []
        if parsed.get("document_count", 1) > 1:
            warnings.append(
                _("Azure detectó más de una factura; solo se aplicó la primera.")
            )

        confidence = float(parsed.get("confidence") or 0.0)
        if confidence < company.vendor_bill_ocr_confidence_threshold:
            warnings.append(
                _("La confianza OCR (%s%%) está por debajo del mínimo configurado.")
                % round(confidence * 100, 2)
            )
        invoice_date = self._vendor_bill_ocr_parse_date(parsed.get("invoice_date"))
        due_date = self._vendor_bill_ocr_parse_date(parsed.get("due_date"))
        today = fields.Date.context_today(self)
        if not invoice_date:
            warnings.append(_("No se identificó una fecha de factura válida."))
        else:
            if invoice_date < today - timedelta(days=company.vendor_bill_ocr_max_age_days):
                warnings.append(_("La fecha de la factura es demasiado antigua."))
            if invoice_date > today + timedelta(days=company.vendor_bill_ocr_future_days):
                warnings.append(_("La fecha de la factura está en el futuro."))
        if due_date and invoice_date and due_date < invoice_date:
            warnings.append(_("La fecha de vencimiento es anterior a la factura."))

        invoice_total = parsed.get("invoice_total")
        subtotal = parsed.get("subtotal")
        tax_total = parsed.get("tax_total")
        if invoice_total is False or invoice_total <= 0:
            warnings.append(_("No se identificó un total positivo."))
        if company.vendor_bill_ocr_max_amount and invoice_total:
            if invoice_total > company.vendor_bill_ocr_max_amount:
                warnings.append(_("El total supera el máximo configurado sin aviso."))
        if (
            invoice_total is not False
            and subtotal is not False
            and tax_total is not False
            and abs((subtotal + tax_total) - invoice_total)
            > company.vendor_bill_ocr_amount_tolerance
        ):
            warnings.append(_("Base + impuestos no coincide con el total detectado."))

        currency = self.currency_id or company.currency_id
        currency_code = (parsed.get("currency") or "").upper()
        if currency_code:
            detected_currency = self.env["res.currency"].sudo().search(
                [("name", "=", currency_code), ("active", "=", True)], limit=1
            )
            if detected_currency:
                currency = detected_currency
            else:
                warnings.append(_("La divisa %s no existe o no está activa.") % currency_code)

        partner, partner_warning = self._vendor_bill_ocr_find_vendor(parsed)
        if partner_warning:
            warnings.append(partner_warning)
        if not parsed.get("vendor_name"):
            warnings.append(_("No se identificó el nombre del proveedor."))
        if not partner:
            warnings.append(_("No se pudo asociar un proveedor de Odoo."))
        if parsed.get("customer_vat") and company.vat:
            if not self._vendor_bill_ocr_tax_ids_match(
                parsed["customer_vat"], company.vat
            ):
                warnings.append(
                    _("El NIF/VAT del cliente de la factura no coincide con la compañía.")
                )

        invoice_id = parsed.get("invoice_id")
        if not invoice_id:
            warnings.append(_("No se identificó el número de factura del proveedor."))
        values = {
            "vendor_bill_ocr_provider": "azure",
            "vendor_bill_ocr_confidence": confidence * 100,
            "vendor_bill_ocr_vendor_name": parsed.get("vendor_name"),
            "vendor_bill_ocr_vendor_vat": parsed.get("vendor_vat"),
            "vendor_bill_ocr_customer_vat": parsed.get("customer_vat"),
            "vendor_bill_ocr_vendor_address": parsed.get("vendor_address"),
            "vendor_bill_ocr_subtotal": subtotal or 0.0,
            "vendor_bill_ocr_tax_total": tax_total or 0.0,
            "vendor_bill_ocr_invoice_total": invoice_total or 0.0,
            "vendor_bill_ocr_detected_iban": parsed.get("iban"),
            "vendor_bill_ocr_payment_term": parsed.get("payment_term"),
            "vendor_bill_ocr_processed_pages": parsed.get("page_count") or 0,
            "currency_id": currency.id,
            "to_check": True,
        }
        if partner:
            values["partner_id"] = partner.id
        if invoice_date:
            values["invoice_date"] = invoice_date
        if due_date:
            values.update(
                {"invoice_payment_term_id": False, "invoice_date_due": due_date}
            )
        if invoice_id:
            values.update({"ref": invoice_id, "payment_reference": invoice_id})
        if parsed.get("purchase_order"):
            values["invoice_origin"] = parsed["purchase_order"]
        self.sudo().with_company(company).write(values)

        iban_warning = self._vendor_bill_ocr_apply_safe_iban(partner, parsed.get("iban"))
        if iban_warning:
            warnings.append(iban_warning)

        global_rates = sorted(
            {
                round(detail["rate"], 4)
                for detail in parsed.get("tax_details") or []
                if detail.get("rate") is not None
            }
            | {
                round(item["tax_rate"], 4)
                for item in parsed.get("items") or []
                if item.get("tax_rate") is not None
            }
        )
        inferred_rate = False
        if not global_rates:
            global_rates, inferred_rate, rate_warnings = (
                self._vendor_bill_ocr_infer_single_tax_rate(parsed)
            )
            warnings.extend(rate_warnings)
        self.sudo().write(
            {
                "vendor_bill_ocr_tax_rates": ", ".join(
                    "%s%%%s"
                    % (
                        "%g" % rate,
                        _(" (inferido)") if inferred_rate else "",
                    )
                    for rate in global_rates
                )
                or False
            }
        )
        line_commands, line_warnings = self._vendor_bill_ocr_prepare_lines(
            parsed, partner, global_rates
        )
        warnings.extend(line_warnings)
        self.sudo().with_company(company).with_context(check_move_validity=False).write(
            {"invoice_line_ids": [(5, 0, 0)] + line_commands}
        )

        if not self.invoice_line_ids:
            warnings.append(_("No se pudo generar ninguna línea de factura."))
        if invoice_total is not False and abs(self.amount_total - invoice_total) > (
            company.vendor_bill_ocr_amount_tolerance
        ):
            warnings.append(
                _(
                    "El total calculado por Odoo (%s) no coincide con el detectado (%s)."
                )
                % (
                    "%s %s" % (round(self.amount_total, 2), currency.name),
                    "%s %s" % (round(invoice_total, 2), currency.name),
                )
            )
        if subtotal is not False and abs(self.amount_untaxed - subtotal) > (
            company.vendor_bill_ocr_amount_tolerance
        ):
            warnings.append(_("La base calculada por Odoo no coincide con la detectada."))
        if tax_total is not False and abs(self.amount_tax - tax_total) > (
            company.vendor_bill_ocr_amount_tolerance
        ):
            warnings.append(_("Los impuestos calculados por Odoo no coinciden con los detectados."))

        duplicate = self._vendor_bill_ocr_find_semantic_duplicate(
            partner, invoice_id, invoice_date, invoice_total, currency
        )
        self.sudo().write({"vendor_bill_ocr_duplicate_id": duplicate.id or False})
        if duplicate:
            warnings.append(
                _("Existe una posible factura duplicada: %s.") % duplicate.display_name
            )

        if company.vendor_bill_ocr_require_review:
            warnings.append(_("La configuración exige una revisión humana antes de contabilizar."))
        if company.vendor_bill_ocr_store_raw_response and raw_response is not None:
            raw_value = json.dumps(raw_response, ensure_ascii=False, separators=(",", ":"))
        else:
            raw_value = False
        processed_at = fields.Datetime.now()
        final_state = "review" if warnings else "done"
        self.sudo().write(
            {
                "vendor_bill_ocr_state": final_state,
                "vendor_bill_ocr_warning": "\n".join(dict.fromkeys(warnings)) or False,
                "vendor_bill_ocr_error": False,
                "vendor_bill_ocr_operation_url": False,
                "vendor_bill_ocr_next_retry": False,
                "vendor_bill_ocr_attempts": 0,
                "vendor_bill_ocr_processed_at": processed_at,
                "vendor_bill_ocr_raw_response": raw_value,
            }
        )
        log = usage_log or self.vendor_bill_ocr_usage_log_id
        if log:
            log.sudo().write(
                {
                    "status": "succeeded",
                    "page_count": parsed.get("page_count") or 0,
                    "error": False,
                }
            )
        if warnings:
            self.message_post(
                body=_("OCR completado. La factura requiere revisión: %s")
                % "; ".join(dict.fromkeys(warnings))
            )
        else:
            self.message_post(body=_("OCR completado sin avisos."))

    def _vendor_bill_ocr_infer_single_tax_rate(self, parsed):
        """Infer one safe tax rate when Azure only returns base and tax total.

        A weighted rate must never be assigned to a mixed-tax invoice.  The
        inferred percentage is therefore accepted only when Azure has not
        returned several tax amounts and it matches an active Odoo purchase tax
        within the configured tolerance.
        """
        self.ensure_one()
        warnings = []
        subtotal = parsed.get("subtotal")
        tax_total = parsed.get("tax_total")
        amount_tolerance = self.company_id.vendor_bill_ocr_amount_tolerance
        if tax_total is False or tax_total is None or abs(tax_total) <= amount_tolerance:
            return [], False, warnings
        if subtotal is False or subtotal is None or subtotal <= 0 or tax_total < 0:
            warnings.append(
                _(
                    "Azure detectó impuestos, pero no devolvió un porcentaje y "
                    "no se pudo inferir de forma segura."
                )
            )
            return [], False, warnings

        positive_details = [
            detail
            for detail in parsed.get("tax_details") or []
            if detail.get("amount") is not False
            and detail.get("amount") is not None
            and abs(detail["amount"]) > amount_tolerance
        ]
        if len(positive_details) > 1:
            warnings.append(
                _(
                    "Azure devolvió varios importes de impuesto sin sus porcentajes; "
                    "no se asignó un IVA automáticamente."
                )
            )
            return [], False, warnings

        inferred_rate = round((tax_total / subtotal) * 100.0, 4)
        if inferred_rate <= 0 or inferred_rate > 100:
            warnings.append(
                _(
                    "El porcentaje de impuesto inferido (%s%%) no es válido; "
                    "revise base e impuestos."
                )
                % ("%g" % inferred_rate)
            )
            return [], False, warnings

        tax = self._vendor_bill_ocr_find_purchase_tax(inferred_rate)
        if not tax:
            warnings.append(
                _(
                    "Azure no devolvió el porcentaje de IVA. El tipo inferido "
                    "(%s%%) no coincide con ningún impuesto de compra configurado; "
                    "no se aplicó automáticamente."
                )
                % ("%g" % inferred_rate)
            )
            return [], False, warnings

        mapped_rate = round(tax.amount, 4)
        warnings.append(
            _(
                "Azure no devolvió el porcentaje de IVA; se infirió %s%% a partir "
                "de la base y del total de impuestos y se vinculó con «%s»."
            )
            % ("%g" % inferred_rate, tax.display_name)
        )
        return [mapped_rate], True, warnings

    def _vendor_bill_ocr_prepare_lines(self, parsed, partner, global_rates):
        self.ensure_one()
        warnings = []
        items = parsed.get("items") or []
        commands = []
        if not items:
            warnings.append(
                _("Azure no desglosó líneas; se creó una línea resumen para revisar.")
            )
            base = parsed.get("subtotal")
            if base is False:
                total = parsed.get("invoice_total")
                taxes = parsed.get("tax_total")
                base = total - taxes if total is not False and taxes is not False else total
            items = [
                {
                    "description": parsed.get("vendor_name") or _("Factura de proveedor"),
                    "quantity": 1.0,
                    "unit_price": base,
                    "amount": base,
                    "tax_rate": global_rates[0] if len(global_rates) == 1 else None,
                    "product_code": False,
                    "confidence": parsed.get("confidence") or 0.0,
                }
            ]
            if len(global_rates) > 1:
                warnings.append(
                    _("Hay varios impuestos y no se pueden distribuir en una línea resumen.")
                )
        for position, item in enumerate(items, start=1):
            vals, item_warnings = self._vendor_bill_ocr_prepare_line_values(
                item, partner, global_rates, position
            )
            warnings.extend(item_warnings)
            commands.append((0, 0, vals))
        return commands, warnings

    def _vendor_bill_ocr_prepare_line_values(
        self, item, partner, global_rates, position
    ):
        self.ensure_one()
        company = self.company_id
        warnings = []
        description = item.get("description") or item.get("product_code") or _(
            "Línea OCR %s"
        ) % position
        rule = self._vendor_bill_ocr_find_mapping_rule(description, partner)
        product = rule.product_id if rule and rule.product_id else self._vendor_bill_ocr_find_product(
            item.get("product_code"), partner
        )
        if not product and not item.get("product_code"):
            product = company.vendor_bill_ocr_default_product_id
        if item.get("product_code") and not product:
            warnings.append(
                _("Línea %s: no se encontró el producto %s.")
                % (position, item["product_code"])
            )
        account = rule.account_id if rule and rule.account_id else self.env["account.account"]
        if not account and product:
            try:
                account = product.product_tmpl_id.get_product_accounts(
                    fiscal_pos=self.fiscal_position_id
                ).get("expense")
            except TypeError:  # Compatibility with older Odoo 16 builds.
                account = product.product_tmpl_id.get_product_accounts(
                    self.fiscal_position_id
                ).get("expense")
        account = account or company.vendor_bill_ocr_default_account_id
        if not account:
            warnings.append(_("Línea %s: falta la cuenta de gasto.") % position)

        quantity = item.get("quantity")
        quantity = quantity if quantity not in (False, None, 0) else 1.0
        unit_price = item.get("unit_price")
        amount = item.get("amount")
        if unit_price is False and amount is not False:
            unit_price = amount / quantity
        if unit_price is False:
            unit_price = 0.0
            warnings.append(_("Línea %s: no se identificó el precio.") % position)
        elif amount is not False and abs((unit_price * quantity) - amount) > (
            company.vendor_bill_ocr_amount_tolerance
        ):
            warnings.append(
                _("Línea %s: cantidad × precio no coincide con el importe detectado.")
                % position
            )

        taxes = self.env["account.tax"]
        rate = item.get("tax_rate")
        if rate is None and len(global_rates) == 1:
            rate = global_rates[0]
        rule_taxes = (
            rule.tax_ids.filtered(
                lambda tax: tax.company_id == company
                and tax.type_tax_use in ("purchase", "all")
                and tax.active
            )
            if rule and rule.tax_ids
            else self.env["account.tax"]
        )
        product_taxes = (
            product.supplier_taxes_id.filtered(
                lambda tax: tax.company_id == company
                and tax.type_tax_use in ("purchase", "all")
                and tax.active
            )
            if product
            else self.env["account.tax"]
        )

        if rate is not None:
            tolerance = company.vendor_bill_ocr_tax_rate_tolerance
            rate_taxes = self._vendor_bill_ocr_filter_taxes_by_rate(rule_taxes, rate, tolerance)
            if not rate_taxes:
                rate_taxes = self._vendor_bill_ocr_filter_taxes_by_rate(
                    product_taxes, rate, tolerance
                )
            if not rate_taxes:
                rate_taxes = self._vendor_bill_ocr_find_purchase_tax(rate)
            if rate_taxes:
                taxes = rate_taxes
            elif rate:
                warnings.append(
                    _("Línea %s: no existe un impuesto de compra del %s%%.")
                    % (position, rate)
                )
        else:
            taxes = rule_taxes or product_taxes
        values = {
            "name": str(description)[:1000],
            "quantity": quantity,
            "price_unit": unit_price,
            "tax_ids": [(6, 0, taxes.ids)],
        }
        if product:
            values["product_id"] = product.id
            values["product_uom_id"] = product.uom_po_id.id
        if account:
            values["account_id"] = account.id
        return values, warnings

    @api.model
    def _vendor_bill_ocr_filter_taxes_by_rate(self, taxes, rate, tolerance):
        matched = taxes.filtered(
            lambda tax: tax.amount_type == "percent" and abs(tax.amount - rate) <= tolerance
        )
        return matched.sorted(key=lambda tax: (abs(tax.amount - rate), tax.sequence, tax.id))[:1]

    def _vendor_bill_ocr_find_vendor(self, parsed):
        self.ensure_one()
        Partner = self.env["res.partner"].sudo().with_context(active_test=True)
        company_domain = [
            "|",
            ("company_id", "=", False),
            ("company_id", "=", self.company_id.id),
        ]
        tax_id = parsed.get("vendor_vat")
        if tax_id:
            normalized = self._vendor_bill_ocr_normalize_tax_id(tax_id)
            suffix = normalized[-8:] if len(normalized) >= 8 else normalized
            candidates = Partner.search(
                company_domain
                + [
                    ("vat", "!=", False),
                    "|",
                    ("vat", "=ilike", tax_id),
                    ("vat", "ilike", suffix),
                ],
                limit=100,
            )
            matches = candidates.filtered(
                lambda partner: self._vendor_bill_ocr_tax_ids_match(
                    partner.vat, tax_id
                )
            ).mapped("commercial_partner_id")
            matches = Partner.browse(list(dict.fromkeys(matches.ids))).exists()
            if len(matches) == 1:
                if not matches.supplier_rank:
                    matches.supplier_rank = 1
                return matches, False
            if len(matches) > 1:
                return Partner.browse(), _(
                    "Hay varios proveedores con el NIF/VAT detectado."
                )

        vendor_name = parsed.get("vendor_name")
        if vendor_name:
            normalized_name = self._vendor_bill_ocr_normalize_text(vendor_name)
            name_candidates = Partner.search(
                company_domain
                + [("supplier_rank", ">", 0), ("name", "=ilike", vendor_name)],
                limit=100,
            ).mapped("commercial_partner_id")
            name_candidates = Partner.browse(
                list(dict.fromkeys(name_candidates.ids))
            ).filtered(
                lambda partner: self._vendor_bill_ocr_normalize_text(partner.name)
                == normalized_name
            )
            if len(name_candidates) == 1:
                return name_candidates, False
            if len(name_candidates) > 1:
                return Partner.browse(), _(
                    "Hay varios proveedores con el nombre detectado."
                )

        if self.company_id.vendor_bill_ocr_auto_create_vendor and tax_id:
            try:
                with self.env.cr.savepoint():
                    partner = Partner.create(
                        {
                            "name": vendor_name or tax_id,
                            "vat": tax_id,
                            "supplier_rank": 1,
                            "company_type": "company",
                            "company_id": self.company_id.id,
                        }
                    )
                return partner, _(
                    "Se creó automáticamente el proveedor; revise sus datos."
                )
            except (ValidationError, UserError) as error:
                return Partner.browse(), _(
                    "No se pudo crear el proveedor con el NIF/VAT detectado: %s"
                ) % str(error)
        return Partner.browse(), False

    def _vendor_bill_ocr_apply_safe_iban(self, partner, detected_iban):
        self.ensure_one()
        if not detected_iban:
            return False
        if not partner:
            return _("Se detectó un IBAN, pero no hay proveedor para validarlo.")
        matched_bank = partner.commercial_partner_id.bank_ids.filtered(
            lambda bank: self._vendor_bill_ocr_normalize_iban(bank.acc_number)
            == detected_iban
        )[:1]
        if matched_bank:
            self.sudo().write({"partner_bank_id": matched_bank.id})
            return False
        # Never create a bank or overwrite one from OCR: invoice fraud control.
        return _(
            "El IBAN detectado no figura en el proveedor. No se ha creado ni modificado "
            "ninguna cuenta bancaria."
        )

    def _vendor_bill_ocr_find_mapping_rule(self, description, partner):
        self.ensure_one()
        rules = self.env["snk.vendor.bill.ocr.mapping.rule"].sudo().search(
            [("company_id", "=", self.company_id.id), ("active", "=", True)],
            order="sequence, id",
        )
        return next(
            (rule for rule in rules if rule.matches(description, partner)),
            rules.browse(),
        )

    def _vendor_bill_ocr_find_product(self, product_code, partner):
        self.ensure_one()
        if not product_code:
            return self.env["product.product"]
        Product = self.env["product.product"].sudo()
        if partner and "product.supplierinfo" in self.env:
            supplier_infos = self.env["product.supplierinfo"].sudo().search(
                [
                    ("partner_id", "child_of", partner.commercial_partner_id.id),
                    ("product_code", "=ilike", product_code),
                ],
                limit=2,
            )
            products = Product.browse()
            for info in supplier_infos:
                product = info.product_id or info.product_tmpl_id.product_variant_id
                products |= product
            if len(products) == 1:
                return products
        products = Product.search(
            [
                ("default_code", "=ilike", product_code),
                ("purchase_ok", "=", True),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.company_id.id),
            ],
            limit=2,
        )
        return products if len(products) == 1 else Product.browse()

    def _vendor_bill_ocr_find_purchase_tax(self, rate):
        self.ensure_one()
        company = self.company_id
        tolerance = company.vendor_bill_ocr_tax_rate_tolerance
        taxes = self.env["account.tax"].sudo().search(
            [
                ("company_id", "=", company.id),
                ("type_tax_use", "in", ("purchase", "all")),
                ("amount_type", "=", "percent"),
                ("active", "=", True),
                ("amount", ">=", rate - tolerance),
                ("amount", "<=", rate + tolerance),
            ]
        )
        taxes = taxes.sorted(
            key=lambda tax: (
                tax.price_include != company.vendor_bill_ocr_prices_include_tax,
                tax.type_tax_use != "purchase",
                bool(tax.include_base_amount),
                abs(tax.amount - rate),
                tax.sequence,
                tax.id,
            )
        )
        return taxes[:1]

    def _vendor_bill_ocr_find_semantic_duplicate(
        self, partner, invoice_id, invoice_date, invoice_total, currency
    ):
        self.ensure_one()
        domain = [
            ("id", "!=", self.id),
            ("company_id", "=", self.company_id.id),
            ("move_type", "in", ("in_invoice", "in_refund")),
            ("state", "!=", "cancel"),
        ]
        if partner and invoice_id:
            return self.sudo().search(
                domain
                + [
                    ("commercial_partner_id", "=", partner.commercial_partner_id.id),
                    ("ref", "=ilike", invoice_id),
                ],
                limit=1,
            )
        if partner and invoice_date and invoice_total is not False:
            tolerance = self.company_id.vendor_bill_ocr_amount_tolerance
            return self.sudo().search(
                domain
                + [
                    ("commercial_partner_id", "=", partner.commercial_partner_id.id),
                    ("invoice_date", "=", invoice_date),
                    ("currency_id", "=", currency.id),
                    ("amount_total", ">=", invoice_total - tolerance),
                    ("amount_total", "<=", invoice_total + tolerance),
                ],
                limit=1,
            )
        return self.browse()

    @api.model
    def _vendor_bill_ocr_parse_date(self, value):
        if not value:
            return False
        try:
            return fields.Date.to_date(value)
        except (TypeError, ValueError):
            return False

    @api.model
    def _vendor_bill_ocr_normalize_text(self, value):
        value = unicodedata.normalize("NFKD", str(value or ""))
        value = "".join(char for char in value if not unicodedata.combining(char))
        return re.sub(r"[^A-Z0-9]", "", value.upper())

    @api.model
    def _vendor_bill_ocr_normalize_tax_id(self, value):
        return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())

    @api.model
    def _vendor_bill_ocr_tax_id_variants(self, value):
        normalized = self._vendor_bill_ocr_normalize_tax_id(value)
        variants = {normalized} if normalized else set()
        if len(normalized) > 8 and normalized[:2].isalpha():
            variants.add(normalized[2:])
        return variants

    @api.model
    def _vendor_bill_ocr_tax_ids_match(self, first, second):
        return bool(
            self._vendor_bill_ocr_tax_id_variants(first)
            & self._vendor_bill_ocr_tax_id_variants(second)
        )

    @api.model
    def _vendor_bill_ocr_normalize_iban(self, value):
        normalized = re.sub(r"[^A-Z0-9]", "", str(value or "").upper())
        if not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", normalized):
            return False
        return normalized
