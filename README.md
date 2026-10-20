# Arab-erp Theme

A standalone Frappe app containing the AR logo, favicon, and navy-blue theme used by Heavy Equipment Rental. It contains no rental DocTypes, workflows, or business logic.

## Assets

- `arab_erp_theme/public/branding/logo.png`: transparent AR logo for the Desk navbar, login page, and splash screen.
- `arab_erp_theme/public/branding/favicon.ico`: matching browser icon.
- `arab_erp_theme/public/css/theme.css`: Desk light and dark palette.
- `arab_erp_theme/public/css/login.css`: login screen styling, scoped to the login page.

The install and migrate hooks set the logo, favicon, and “Arab ERP” app name only when those fields are empty or still use Frappe/ERPNext defaults. Existing custom site branding remains in place.

## Install on a site

From the Bench containing this app:

```sh
bench --site your-site.example install-app arab_erp_theme
bench --site your-site.example clear-cache
```

The app can be installed independently of Heavy Equipment Rental. Avoid installing both on one site because both provide site-wide branding and Desk styles.
