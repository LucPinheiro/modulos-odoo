import base64
import copy
from unittest.mock import Mock, patch

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestVendorBillOcr(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.account = cls.env["account.account"].create(
            {
                "name": "Gastos OCR pruebas",
                "code": "OCR600000",
                "account_type": "expense",
                "company_id": cls.company.id,
            }
        )
        cls.journal = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "purchase")],
            limit=1,
        )
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create(
                {
                    "name": "Compras OCR",
                    "code": "OCRP",
                    "type": "purchase",
                    "company_id": cls.company.id,
                }
            )
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "IVA compras OCR 21%",
                "amount": 21.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "company_id": cls.company.id,
            }
        )
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Proveedor OCR Pruebas SL",
                "vat": "B12345678",
                "supplier_rank": 1,
            }
        )
        cls.company.write(
            {
                "vendor_bill_ocr_enabled": True,
                "vendor_bill_ocr_azure_endpoint": "https://ocr-tests.cognitiveservices.azure.com",
                "vendor_bill_ocr_default_account_id": cls.account.id,
                "vendor_bill_ocr_auto_tax": True,
                "vendor_bill_ocr_require_review": True,
                "vendor_bill_ocr_confidence_threshold": 0.75,
                "vendor_bill_ocr_max_pages": 2,
                "vendor_bill_ocr_daily_limit": 50,
                "vendor_bill_ocr_monthly_limit": 500,
            }
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "snk_vendor_bill_ocr.azure_key.%s" % cls.company.id, "test-key"
        )

    def _new_bill(self, ocr_state="pending", with_attachment=True):
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "company_id": self.company.id,
                "journal_id": self.journal.id,
                "currency_id": self.company.currency_id.id,
                "ref": "pendiente-ocr",
                "to_check": True,
            }
        )
        values = {
            "vendor_bill_ocr_state": ocr_state,
            "vendor_bill_ocr_provider": "azure",
        }
        if with_attachment:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": "factura.jpg",
                    "datas": base64.b64encode(b"\xff\xd8\xff\xe0test-invoice"),
                    "mimetype": "image/jpeg",
                    "res_model": "account.move",
                    "res_id": bill.id,
                }
            )
            values["vendor_bill_ocr_source_attachment_id"] = attachment.id
        bill.write(values)
        return bill

    @staticmethod
    def _azure_result(iban="ES9121000418450200051332"):
        return {
            "status": "succeeded",
            "analyzeResult": {
                "pages": [{"pageNumber": 1}],
                "content": "Proveedor OCR Pruebas SL NIF B12345678",
                "documents": [
                    {
                        "docType": "invoice",
                        "confidence": 0.98,
                        "fields": {
                            "VendorName": {
                                "type": "string",
                                "valueString": "Proveedor OCR Pruebas SL",
                                "confidence": 0.98,
                            },
                            "VendorTaxId": {
                                "type": "string",
                                "valueString": "B12345678",
                                "confidence": 0.97,
                            },
                            "CustomerTaxId": {
                                "type": "string",
                                "valueString": "A00000000",
                                "confidence": 0.96,
                            },
                            "InvoiceId": {
                                "type": "string",
                                "valueString": "F-2026-001",
                                "confidence": 0.99,
                            },
                            "InvoiceDate": {
                                "type": "date",
                                "valueDate": "2026-08-20",
                                "confidence": 0.98,
                            },
                            "DueDate": {
                                "type": "date",
                                "valueDate": "2026-09-20",
                                "confidence": 0.96,
                            },
                            "PurchaseOrder": {
                                "type": "string",
                                "valueString": "PO-77",
                            },
                            "SubTotal": {
                                "type": "currency",
                                "valueCurrency": {"amount": 100.0, "currencyCode": "EUR"},
                                "confidence": 0.98,
                            },
                            "TotalTax": {
                                "type": "currency",
                                "valueCurrency": {"amount": 21.0, "currencyCode": "EUR"},
                                "confidence": 0.98,
                            },
                            "InvoiceTotal": {
                                "type": "currency",
                                "valueCurrency": {"amount": 121.0, "currencyCode": "EUR"},
                                "confidence": 0.99,
                            },
                            "PaymentDetails": {
                                "type": "array",
                                "valueArray": [
                                    {
                                        "type": "object",
                                        "valueObject": {
                                            "IBAN": {"type": "string", "valueString": iban}
                                        },
                                    }
                                ],
                            },
                            "TaxDetails": {
                                "type": "array",
                                "valueArray": [
                                    {
                                        "type": "object",
                                        "valueObject": {
                                            "Amount": {
                                                "type": "currency",
                                                "valueCurrency": {"amount": 21.0},
                                            },
                                            "Rate": {
                                                "type": "string",
                                                "valueString": "21 %",
                                            },
                                        },
                                    }
                                ],
                            },
                            "Items": {
                                "type": "array",
                                "valueArray": [
                                    {
                                        "type": "object",
                                        "valueObject": {
                                            "Description": {
                                                "type": "string",
                                                "valueString": "Servicios profesionales",
                                                "confidence": 0.97,
                                            },
                                            "Quantity": {
                                                "type": "number",
                                                "valueNumber": 1,
                                                "confidence": 0.96,
                                            },
                                            "UnitPrice": {
                                                "type": "currency",
                                                "valueCurrency": {"amount": 100.0},
                                                "confidence": 0.98,
                                            },
                                            "Amount": {
                                                "type": "currency",
                                                "valueCurrency": {"amount": 100.0},
                                                "confidence": 0.98,
                                            },
                                            "TaxRate": {
                                                "type": "string",
                                                "valueString": "21%",
                                            },
                                        },
                                    }
                                ],
                            },
                        },
                    }
                ],
            },
        }

    def test_parse_invoice_schema(self):
        parsed = self.env["account.move"]._vendor_bill_ocr_parse_azure_result(
            self._azure_result()
        )
        self.assertEqual(parsed["vendor_name"], "Proveedor OCR Pruebas SL")
        self.assertEqual(parsed["vendor_vat"], "B12345678")
        self.assertEqual(parsed["invoice_id"], "F-2026-001")
        self.assertEqual(parsed["invoice_total"], 121.0)
        self.assertEqual(parsed["tax_details"][0]["rate"], 21.0)
        self.assertEqual(parsed["items"][0]["unit_price"], 100.0)
        self.assertEqual(parsed["iban"], "ES9121000418450200051332")

    def test_apply_result_creates_reviewable_bill(self):
        bill = self._new_bill()
        parsed = bill._vendor_bill_ocr_parse_azure_result(self._azure_result())
        bill._vendor_bill_ocr_apply_result(parsed, self._azure_result())
        self.assertEqual(bill.partner_id, self.vendor)
        self.assertEqual(bill.ref, "F-2026-001")
        self.assertEqual(bill.invoice_origin, "PO-77")
        self.assertEqual(len(bill.invoice_line_ids), 1)
        self.assertEqual(bill.invoice_line_ids.tax_ids.amount, 21.0)
        self.assertAlmostEqual(bill.amount_total, 121.0, places=2)
        self.assertEqual(bill.vendor_bill_ocr_state, "review")
        self.assertEqual(bill.state, "draft")

    def test_infers_single_vat_rate_when_azure_omits_percentages(self):
        response = copy.deepcopy(self._azure_result())
        fields = response["analyzeResult"]["documents"][0]["fields"]
        del fields["TaxDetails"]["valueArray"][0]["valueObject"]["Rate"]
        del fields["Items"]["valueArray"][0]["valueObject"]["TaxRate"]

        bill = self._new_bill()
        parsed = bill._vendor_bill_ocr_parse_azure_result(response)
        bill._vendor_bill_ocr_apply_result(parsed, response)

        self.assertEqual(bill.invoice_line_ids.tax_ids.amount, 21.0)
        self.assertAlmostEqual(bill.amount_tax, 21.0, places=2)
        self.assertAlmostEqual(bill.amount_total, 121.0, places=2)
        self.assertEqual(bill.vendor_bill_ocr_tax_rates, "21% (inferido)")
        self.assertIn("se infirió 21%", bill.vendor_bill_ocr_warning)

    def test_does_not_assign_unmatched_effective_tax_rate(self):
        response = copy.deepcopy(self._azure_result())
        fields = response["analyzeResult"]["documents"][0]["fields"]
        fields["TotalTax"]["valueCurrency"]["amount"] = 15.5
        fields["InvoiceTotal"]["valueCurrency"]["amount"] = 115.5
        del fields["TaxDetails"]["valueArray"][0]["valueObject"]["Rate"]
        del fields["Items"]["valueArray"][0]["valueObject"]["TaxRate"]

        bill = self._new_bill()
        parsed = bill._vendor_bill_ocr_parse_azure_result(response)
        bill._vendor_bill_ocr_apply_result(parsed, response)

        self.assertFalse(bill.invoice_line_ids.tax_ids)
        self.assertFalse(bill.vendor_bill_ocr_tax_rates)
        self.assertIn("no coincide con ningún impuesto", bill.vendor_bill_ocr_warning)

    def test_product_purchase_tax_has_priority_for_same_rate(self):
        preferred_tax = self.env["account.tax"].create(
            {
                "name": "IVA compras OCR 21% con etiquetas preferidas",
                "amount": 21.0,
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "company_id": self.company.id,
            }
        )
        product = self.env["product.product"].create(
            {
                "name": "Servicio OCR con IVA configurado",
                "purchase_ok": True,
                "supplier_taxes_id": [(6, 0, preferred_tax.ids)],
            }
        )
        self.company.vendor_bill_ocr_default_product_id = product

        bill = self._new_bill()
        parsed = bill._vendor_bill_ocr_parse_azure_result(self._azure_result())
        bill._vendor_bill_ocr_apply_result(parsed)

        self.assertEqual(bill.invoice_line_ids.tax_ids, preferred_tax)

    def test_tax_numeric_edge_cases_are_preserved(self):
        parser = self.env["account.move"]
        self.assertEqual(parser._vendor_bill_ocr_percent_to_float(1), 1.0)
        self.assertEqual(parser._vendor_bill_ocr_percent_to_float(0.21), 21.0)
        self.assertEqual(parser._vendor_bill_ocr_to_float(0), 0.0)

    def test_mark_reviewed_then_post_is_unblocked(self):
        bill = self._new_bill()
        parsed = bill._vendor_bill_ocr_parse_azure_result(self._azure_result())
        bill._vendor_bill_ocr_apply_result(parsed)
        bill.action_vendor_bill_ocr_mark_reviewed()
        self.assertEqual(bill.vendor_bill_ocr_state, "done")
        self.assertFalse(bill.to_check)
        self.assertEqual(bill.vendor_bill_ocr_reviewed_by_id, self.env.user)

    def test_post_is_blocked_while_reviewing(self):
        bill = self._new_bill(ocr_state="review")
        with self.assertRaises(UserError):
            bill.action_post()

    def test_endpoint_security(self):
        with self.assertRaises(ValidationError):
            self.company._vendor_bill_ocr_validate_azure_url("http://localhost:8080")
        with self.assertRaises(ValidationError):
            self.company._vendor_bill_ocr_validate_azure_url("https://example.com")
        self.assertTrue(
            self.company._vendor_bill_ocr_validate_azure_url(
                "https://ocr-tests.cognitiveservices.azure.com"
            )
        )
        self.assertTrue(
            self.company._vendor_bill_ocr_validate_azure_url(
                "https://ocr-tests.cognitiveservices.azure.com/documentintelligence/"
                "documentModels/prebuilt-invoice/analyzeResults/123?api-version=2024-11-30",
                operation_url=True,
            )
        )

    def test_submit_is_async_and_caps_pages(self):
        bill = self._new_bill()
        response = Mock(status_code=202)
        response.headers = {
            "Operation-Location": "https://ocr-tests.cognitiveservices.azure.com/"
            "documentintelligence/documentModels/prebuilt-invoice/analyzeResults/123"
        }
        with patch(
            "odoo.addons.snk_vendor_bill_ocr.models.account_move.requests.post",
            return_value=response,
        ) as post:
            bill._vendor_bill_ocr_submit_azure()
        self.assertEqual(bill.vendor_bill_ocr_state, "processing")
        self.assertIn("prebuilt-invoice:analyze", post.call_args.args[0])
        self.assertIn("pages=1-2", post.call_args.args[0])
        self.assertEqual(bill.vendor_bill_ocr_usage_log_id.status, "accepted")

    def test_daily_hard_limit_counts_attempts(self):
        self.company.vendor_bill_ocr_daily_limit = 1
        first = self._new_bill()
        second = self._new_bill()
        self.company._vendor_bill_ocr_check_and_log_quota(first)
        with self.assertRaises(UserError):
            self.company._vendor_bill_ocr_check_and_log_quota(second)

    def test_unknown_iban_is_never_created(self):
        bill = self._new_bill()
        parsed = bill._vendor_bill_ocr_parse_azure_result(self._azure_result())
        before = self.env["res.partner.bank"].search_count(
            [("partner_id", "=", self.vendor.id)]
        )
        bill._vendor_bill_ocr_apply_result(parsed)
        after = self.env["res.partner.bank"].search_count(
            [("partner_id", "=", self.vendor.id)]
        )
        self.assertEqual(before, after)
        self.assertIn("IBAN", bill.vendor_bill_ocr_warning)

    def test_mapping_rule_regex(self):
        rule = self.env["snk.vendor.bill.ocr.mapping.rule"].create(
            {
                "name": "Asesoría",
                "company_id": self.company.id,
                "match_type": "regex",
                "pattern": "asesor[ií]a|consultor[ií]a",
                "account_id": self.account.id,
            }
        )
        self.assertTrue(rule.matches("Servicio de consultoría", self.vendor))
        with self.assertRaises(ValidationError):
            rule.pattern = "["

    def test_exact_file_duplicate_is_blocked(self):
        image = base64.b64encode(b"\xff\xd8\xff\xe0same-invoice")
        values = {
            "bill_file": image,
            "bill_filename": "factura.jpg",
            "company_id": self.company.id,
            "journal_id": self.journal.id,
        }
        self.env["snk.vendor.bill.ocr.upload.wizard"].create(values).action_create_bill()
        with self.assertRaises(UserError):
            self.env["snk.vendor.bill.ocr.upload.wizard"].create(
                values
            ).action_create_bill()

    def test_invoice_user_cannot_forge_technical_state(self):
        user = self.env["res.users"].create(
            {
                "name": "Usuario facturas OCR",
                "login": "vendor-bill-ocr-user@test.invalid",
                "groups_id": [
                    (6, 0, [self.env.ref("account.group_account_invoice").id])
                ],
                "company_id": self.company.id,
                "company_ids": [(6, 0, [self.company.id])],
            }
        )
        bill = self._new_bill()
        with self.assertRaises(AccessError):
            bill.with_user(user).write({"vendor_bill_ocr_state": "done"})
