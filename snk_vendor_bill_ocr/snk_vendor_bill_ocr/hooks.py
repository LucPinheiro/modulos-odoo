def uninstall_hook(cr, registry):
    cr.execute(
        "DELETE FROM ir_config_parameter "
        "WHERE key LIKE 'snk_vendor_bill_ocr.azure_key.%'"
    )

