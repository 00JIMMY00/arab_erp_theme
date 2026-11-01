"""Regression checks for filtering, permissions, and currency-safe summaries."""

import unittest
from unittest.mock import patch

import frappe
from frappe.utils import getdate

from arab_erp_theme.arab_erp_theme.report.expense_entry_report.expense_entry_report import execute, get_conditions


class TestExpenseEntryReport(unittest.TestCase):
	def test_zero_amount_bounds_are_kept(self):
		conditions = get_conditions(frappe._dict(min_amount=0, max_amount=0))
		self.assertIn(["Expense Entry Detail", "amount", ">=", 0], conditions)
		self.assertIn(["Expense Entry Detail", "amount", "<=", 0], conditions)

	def test_audit_end_date_includes_entire_day(self):
		conditions = get_conditions(frappe._dict(creation_to_date="2026-10-26"))
		self.assertEqual(conditions, [["Expense Entry", "creation", "<", getdate("2026-10-27")]])

	def test_rejects_reversed_ranges_and_invalid_status(self):
		for filters in (
			{"from_date": "2026-10-27", "to_date": "2026-10-26"},
			{"creation_from_date": "2026-10-27", "creation_to_date": "2026-10-26"},
			{"modified_from_date": "2026-10-27", "modified_to_date": "2026-10-26"},
			{"min_amount": 2, "max_amount": 1}, {"status": "Unknown"},
			{"min_amount": "abc"}, {"max_amount": "NaN"}, {"max_amount": "Infinity"},
		):
			with self.subTest(filters=filters), self.assertRaises(frappe.ValidationError):
				get_conditions(frappe._dict(filters))

	def test_parent_permissions_and_totals_by_currency(self):
		rows = [
			frappe._dict(expense_entry="A", docstatus=1, currency="EGP", amount=100),
			frappe._dict(expense_entry="A", docstatus=1, currency="EGP", amount=25),
			frappe._dict(expense_entry="B", docstatus=1, currency="USD", amount=10),
			frappe._dict(expense_entry="C", docstatus=0, currency="EGP", amount=500),
			frappe._dict(expense_entry="D", docstatus=2, currency="EGP", amount=1000),
		]
		with patch.object(frappe, "get_list", return_value=rows) as query:
			result = execute()
			self.assertEqual(query.call_args.args, ("Expense Entry",))
			self.assertFalse(query.call_args.kwargs.get("ignore_permissions", False))
			self.assertEqual(query.call_args.kwargs["limit_page_length"], 0)
		self.assertEqual(result[4][0]["value"], 4)
		self.assertEqual(result[4][1]["value"], 5)
		self.assertEqual({s["currency"]: s["value"] for s in result[4][2:]}, {"EGP": 125, "USD": 10})
		self.assertEqual([row.status for row in rows], ["Submitted", "Submitted", "Submitted", "Draft", "Cancelled"])
		self.assertTrue(result[5])
		self.assertEqual({r.currency: r.amount for r in result[1] if r.get("is_total_row")}, {"EGP": 1625, "USD": 10})

	def test_grouping_aggregates_lines_and_preserves_summary(self):
		rows = [
			frappe._dict(expense_entry="A", docstatus=1, currency="EGP", cost_center="Main", amount=100),
			frappe._dict(expense_entry="A", docstatus=1, currency="EGP", cost_center="Main", amount=25),
			frappe._dict(expense_entry="B", docstatus=1, currency="EGP", cost_center="Branch", amount=10),
		]
		with patch.object(frappe, "get_list", return_value=rows):
			result = execute({"group_by": "Cost Center"})
		self.assertEqual(result[0][0]["label"], "Cost Center")
		self.assertEqual({r.group_value: r.amount for r in result[1]}, {"Main": 125, "Branch": 10})
		self.assertEqual(result[4][0]["value"], 2)
		self.assertEqual(result[4][1]["value"], 3)
		self.assertFalse(result[5])

	def test_grouping_keeps_different_currencies_separate(self):
		rows = [
			frappe._dict(expense_entry="A", docstatus=1, currency="EGP", mode_of_payment="Cash", amount=100),
			frappe._dict(expense_entry="B", docstatus=1, currency="USD", mode_of_payment="Cash", amount=10),
		]
		with patch.object(frappe, "get_list", return_value=rows):
			result = execute({"group_by": "Mode of Payment"})
		self.assertEqual({r.group_value: r.amount for r in result[1][:2]}, {"Cash (EGP)": 100, "Cash (USD)": 10})
		self.assertTrue(result[5])

	def test_rejects_invalid_group_by(self):
		with self.assertRaises(frappe.ValidationError):
			execute({"group_by": "Unknown"})
