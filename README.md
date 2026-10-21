# Arab-erp Theme

A Frappe app containing the AR logo, favicon, navy-blue theme, and a simple expense posting flow.

## Assets

- `arab_erp_theme/public/branding/logo.png`: transparent AR logo for the Desk navbar, login page, and splash screen.
- `arab_erp_theme/public/branding/favicon.ico`: matching browser icon.
- `arab_erp_theme/public/css/theme.css`: Desk light and dark palette.
- `arab_erp_theme/public/css/login.css`: login screen styling, scoped to the login page.

The install and migrate hooks set the logo, favicon, and “Arab ERP” app name only when those fields are empty or still use Frappe/ERPNext defaults. Existing custom site branding remains in place.

## Expenses

This feature requires ERPNext. Create an **Expense Entry Type** for each expense category, with its company and a non-group Expense account. Then create an **Expense Entry** for the same company with one or more expense rows, a Mode of Payment, and an optional description. The account on each row comes from its Expense Entry Type. The Mode of Payment needs a default account for that company.

Submitting an Expense Entry creates and submits one Journal Entry: it debits each expense account and credits the Mode of Payment account for the total. Cancelling the Expense Entry cancels its Journal Entry. All accounts must use the company's default currency. A linked Journal Entry cannot be cancelled directly while its Expense Entry is submitted.

## Install on a site

From the Bench containing this app:

```sh
bench --site your-site.example install-app arab_erp_theme
bench --site your-site.example clear-cache
```

For an existing installation, run `bench --site your-site.example migrate` to create the new DocTypes.

The Cranes and Heavy Equipment Rental apps also define expense DocTypes with overlapping names. Install this expense flow only on a site that does not use those DocTypes.
