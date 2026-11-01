"""Expense lines, with document permissions and company-specific currencies."""

from collections import defaultdict
from math import isfinite

import frappe
from frappe import _
from frappe.utils import add_days, flt, getdate


STATUSES = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
GROUP_FIELDS = {
	"Company": "company",
	"Cost Center": "cost_center",
	"Expense Entry Type": "expense_entry_type",
	"Expense Entry Account": "expense_entry_account",
	"Mode of Payment": "mode_of_payment",
	"Posting Date": "posting_date",
}


def execute(filters=None):
	filters = frappe._dict(filters or {})
	group_by = filters.get("group_by")
	if group_by and group_by not in GROUP_FIELDS:
		frappe.throw(_("Invalid Group By option."))
	conditions = get_conditions(filters)
	data = frappe.get_list(
		"Expense Entry",
		fields=[
			"name as expense_entry", "posting_date", "company", "company.default_currency as currency",
			"cost_center", "description", "mode_of_payment", "journal_entry", "amended_from", "docstatus",
			"owner", "creation", "modified", "modified_by", "expenses.idx as expense_row",
			"expenses.expense_entry_type as expense_entry_type",
			"expenses.expense_entry_account as expense_entry_account", "expenses.amount as amount",
		],
		filters=conditions,
		order_by="`tabExpense Entry`.posting_date desc, `tabExpense Entry`.name desc, `tabExpense Entry Detail`.idx asc",
		limit_page_length=0,
	)
	status_labels = {0: _("Draft"), 1: _("Submitted"), 2: _("Cancelled")}
	submitted_totals = defaultdict(float)
	for row in data:
		row.status = status_labels[row.docstatus]
		if row.docstatus == 1:
			submitted_totals[row.currency] += flt(row.amount)
	summary = [
		{"label": _("Expense Entries"), "value": len({r.expense_entry for r in data}), "datatype": "Int"},
		{"label": _("Expense Lines"), "value": len(data), "datatype": "Int"},
	]
	for currency, amount in sorted(submitted_totals.items()):
		summary.append({
			"label": _("Submitted Amount ({0})").format(currency), "value": amount,
			"datatype": "Currency", "currency": currency, "indicator": "Blue",
		})
	columns = get_columns()
	if group_by:
		columns, data = group_expenses(data, group_by)

	# The standard footer handles a single currency, including inline table filtering.
	# Separate totals prevent adding amounts in different currencies together.
	totals = defaultdict(float)
	for row in data:
		totals[row.currency] += flt(row.amount)
	skip_total_row = len(totals) > 1
	if skip_total_row:
		data = list(data)
		for currency, amount in sorted(totals.items()):
			data.append(frappe._dict({
				columns[0]["fieldname"]: _("Total ({0})").format(currency),
				"amount": amount, "currency": currency, "is_total_row": True,
			}))
	return columns, data, None, None, summary, skip_total_row


def group_expenses(data, group_by):
	field = GROUP_FIELDS[group_by]
	groups = {}
	multiple_currencies = len({row.currency for row in data}) > 1
	for row in data:
		value = row.get(field)
		key = (value, row.currency)
		if key not in groups:
			label = str(value) if value else _("Not Set")
			if multiple_currencies:
				label = _("{0} ({1})").format(label, row.currency)
			groups[key] = frappe._dict(group_value=label, currency=row.currency, amount=0)
		groups[key].amount += flt(row.amount)
	columns = [
		{"fieldname": "group_value", "label": _(group_by), "fieldtype": "Data", "width": 300},
		{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency", "options": "currency", "width": 160},
	]
	return columns, sorted(groups.values(), key=lambda row: (row.group_value, row.currency))


def get_conditions(filters):
	conditions = []
	for prefix, label in (("", _("Posting Date")), ("creation_", _("Created On")), ("modified_", _("Modified On"))):
		start, end = filters.get(prefix + "from_date"), filters.get(prefix + "to_date")
		if start and end and getdate(start) > getdate(end):
			frappe.throw(_("{0}: From Date must be before or equal to To Date.").format(label))
		field = {"": "posting_date", "creation_": "creation", "modified_": "modified"}[prefix]
		if start:
			conditions.append(["Expense Entry", field, ">=", getdate(start)])
		if end:
			# Datetime end dates include the entire day.
			if prefix:
				conditions.append(["Expense Entry", field, "<", add_days(getdate(end), 1)])
			else:
				conditions.append(["Expense Entry", field, "<=", getdate(end)])

	for field in ("company", "cost_center", "mode_of_payment", "journal_entry", "amended_from", "owner", "modified_by"):
		if filters.get(field):
			conditions.append(["Expense Entry", field, "=", filters[field]])
	if filters.get("expense_entry"):
		conditions.append(["Expense Entry", "name", "=", filters.expense_entry])
	if filters.get("description"):
		conditions.append(["Expense Entry", "description", "like", f"%{filters.description}%"])
	if filters.get("status") and filters.status != "All":
		if filters.status not in STATUSES:
			frappe.throw(_("Invalid Status."))
		conditions.append(["Expense Entry", "docstatus", "=", STATUSES[filters.status]])
	if filters.get("currency"):
		companies = frappe.get_all("Company", filters={"default_currency": filters.currency}, pluck="name")
		# Filter the parent documents so the normal Expense Entry permissions still apply.
		conditions.append(["Expense Entry", "company", "in", companies or [""]])
	for field in ("expense_entry_type", "expense_entry_account"):
		if filters.get(field):
			conditions.append(["Expense Entry Detail", field, "=", filters[field]])
	min_amount, max_amount = filters.get("min_amount"), filters.get("max_amount")
	for value in (min_amount, max_amount):
		if value in (None, ""):
			continue
		try:
			valid = isfinite(float(value))
		except (TypeError, ValueError):
			valid = False
		if not valid:
			frappe.throw(_("Amount filters must be valid numbers."))
	if min_amount not in (None, "") and max_amount not in (None, "") and flt(min_amount) > flt(max_amount):
		frappe.throw(_("Minimum Amount must be less than or equal to Maximum Amount."))
	for value, operator in ((min_amount, ">="), (max_amount, "<=")):
		if value not in (None, ""):
			conditions.append(["Expense Entry Detail", "amount", operator, flt(value)])
	return conditions


def get_columns():
	return [
		{"fieldname": field, "label": _(label), "fieldtype": fieldtype, "width": width, **options}
		for field, label, fieldtype, width, options in [
			("expense_entry", "Expense Entry", "Link", 150, {"options": "Expense Entry"}),
			("posting_date", "Posting Date", "Date", 110, {}),
			("status", "Status", "Data", 100, {}),
			("cost_center", "Cost Center", "Link", 170, {"options": "Cost Center"}),
			("description", "Description", "Data", 260, {}),
			("expense_entry_type", "Expense Entry Type", "Link", 180, {"options": "Expense Entry Type"}),
			("expense_entry_account", "Expense Entry Account", "Link", 210, {"options": "Account"}),
			("amount", "Amount", "Currency", 130, {"options": "currency"}),
			("mode_of_payment", "Mode of Payment", "Link", 160, {"options": "Mode of Payment"}),
			("journal_entry", "Journal Entry", "Link", 180, {"options": "Journal Entry"}),
		]
	]
