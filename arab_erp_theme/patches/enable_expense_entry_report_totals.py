"""Enable the totals footer on existing reports, whose settings Frappe preserves on sync."""

import frappe


def execute():
	if frappe.db.exists("Report", "Expense Entry Report"):
		frappe.db.set_value("Report", "Expense Entry Report", "add_total_row", 1)
