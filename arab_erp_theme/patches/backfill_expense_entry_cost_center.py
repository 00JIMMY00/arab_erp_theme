"""Recover historical cost centers from the posted journal; leave descriptions intact."""

import frappe


def execute():
	for entry in frappe.get_all("Expense Entry", fields=["name", "company", "docstatus", "journal_entry"], filters={"cost_center": ["is", "not set"]}):
		cost_center = None
		if entry.journal_entry:
			centers = frappe.get_all(
				"Journal Entry Account",
				filters={"parent": entry.journal_entry, "parenttype": "Journal Entry", "debit": [">", 0], "cost_center": ["is", "set"]},
				pluck="cost_center",
			)
			if len(set(centers)) == 1:
				cost_center = centers[0]
		elif entry.docstatus == 0:
			cost_center = frappe.db.get_value("Company", entry.company, "cost_center")
		if cost_center:
			frappe.db.set_value("Expense Entry", entry.name, "cost_center", cost_center, update_modified=False)
