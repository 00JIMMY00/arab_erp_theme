"""Apply Arab ERP branding where a site still uses the framework defaults."""

import frappe

LOGO = "/assets/arab_erp_theme/branding/logo.png"
FAVICON = "/assets/arab_erp_theme/branding/favicon.ico"
APP_NAME = "Arab ERP"


def apply_branding():
    defaults = {
        "Navbar Settings": {"app_logo": LOGO},
        "Website Settings": {
            "app_logo": LOGO,
            "favicon": FAVICON,
            "splash_image": LOGO,
            "app_name": APP_NAME,
        },
    }
    changed = False
    for doctype, fields in defaults.items():
        for fieldname, value in fields.items():
            current = frappe.db.get_single_value(doctype, fieldname)
            if current == value:
                continue
            if current and not (
                current.startswith(("/assets/frappe/", "/assets/erpnext/"))
                or (fieldname == "app_name" and current in ("Frappe", "ERPNext"))
            ):
                continue
            frappe.db.set_single_value(doctype, fieldname, value)
            changed = True
    if changed:
        frappe.clear_cache()
