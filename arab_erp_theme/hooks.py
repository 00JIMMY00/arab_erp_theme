"""Arab ERP branding and expense posting hooks."""

app_name = "arab_erp_theme"
app_title = "Arab-erp Theme"
app_publisher = "Arab ERP"
app_description = "AR branding and expense posting for ERPNext"
app_email = "j@gmail.com"
app_license = "mit"
required_apps = ["erpnext"]

app_logo_url = "/assets/arab_erp_theme/branding/logo.png"
app_include_css = "/assets/arab_erp_theme/css/theme.css"
web_include_css = "/assets/arab_erp_theme/css/login.css"
website_context = {
    "favicon": "/assets/arab_erp_theme/branding/favicon.ico",
    "splash_image": "/assets/arab_erp_theme/branding/logo.png",
}

after_install = "arab_erp_theme.branding.apply_branding"
after_migrate = "arab_erp_theme.branding.apply_branding"

doc_events = {
    "Journal Entry": {
        "before_cancel": "arab_erp_theme.arab_erp_theme.doctype.expense_entry.expense_entry.guard_journal_entry_cancel"
    }
}
