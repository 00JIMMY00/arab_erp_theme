"""The Arab ERP logo and theme, without rental-specific functionality."""

app_name = "arab_erp_theme"
app_title = "Arab-erp Theme"
app_publisher = "Arab ERP"
app_description = "Standalone AR branding and navy-blue theme for Frappe and ERPNext"
app_email = "j@gmail.com"
app_license = "mit"

app_logo_url = "/assets/arab_erp_theme/branding/logo.png"
app_include_css = "/assets/arab_erp_theme/css/theme.css"
web_include_css = "/assets/arab_erp_theme/css/login.css"
website_context = {
    "favicon": "/assets/arab_erp_theme/branding/favicon.ico",
    "splash_image": "/assets/arab_erp_theme/branding/logo.png",
}

after_install = "arab_erp_theme.branding.apply_branding"
after_migrate = "arab_erp_theme.branding.apply_branding"
