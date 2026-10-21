import erpnext
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class ExpenseEntry(Document):
	def validate(self):
		if self.journal_entry and self.docstatus == 0:
			frappe.throw(_("The Journal Entry link is set when the Expense Entry is submitted."))
		self.get_accounting_details()

	def on_submit(self):
		if self.journal_entry:
			frappe.throw(_("This Expense Entry already has a Journal Entry."))

		payment_account = self.get_accounting_details()
		cost_center = erpnext.get_default_cost_center(self.company)
		accounts = [
			{
				"account": row.expense_entry_account,
				"debit_in_account_currency": row.amount,
				"cost_center": cost_center,
			}
			for row in self.expenses
		]
		accounts.append({
			"account": payment_account,
			"credit_in_account_currency": sum(flt(row.amount) for row in self.expenses),
		})
		journal = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": self.company,
			"posting_date": self.posting_date,
			"mode_of_payment": self.mode_of_payment,
			"user_remark": _("Expense Entry {0}: {1}").format(self.name, self.description or ""),
			"accounts": accounts,
		})
		journal.flags.ignore_permissions = True
		journal.insert()
		journal.submit()
		self.db_set("journal_entry", journal.name, update_modified=False)

	def on_cancel(self):
		if not self.journal_entry:
			frappe.throw(_("The linked Journal Entry is missing."))
		if not frappe.db.exists("Journal Entry", self.journal_entry):
			frappe.throw(_("Linked Journal Entry {0} is missing.").format(self.journal_entry))
		journal = frappe.get_doc("Journal Entry", self.journal_entry, for_update=True)
		if journal.docstatus != 1:
			frappe.throw(_("Linked Journal Entry {0} is not submitted.").format(journal.name))
		journal.flags.ignore_permissions = True
		journal.cancel()

	def get_accounting_details(self):
		if not self.expenses:
			frappe.throw(_("Add at least one expense row."))
		company_currency = frappe.db.get_value("Company", self.company, "default_currency")
		if not company_currency:
			frappe.throw(_("Select a Company with a default currency."))
		for row in self.expenses:
			row.amount = flt(row.amount, row.precision("amount"))
			if flt(row.amount) <= 0:
				frappe.throw(_("Row {0}: Amount must be greater than zero.").format(row.idx))
			expense_type = frappe.db.get_value(
				"Expense Entry Type", row.expense_entry_type, ["enabled", "company", "account"], as_dict=True
			)
			if not expense_type or not expense_type.enabled or expense_type.company != self.company:
				frappe.throw(_("Row {0}: Select an enabled Expense Entry Type for this Company.").format(row.idx))
			account = frappe.db.get_value(
				"Account", expense_type.account,
				["company", "root_type", "is_group", "account_currency"], as_dict=True,
			)
			if (
				not account or account.company != self.company or account.root_type != "Expense"
				or account.is_group or account.account_currency != company_currency
			):
				frappe.throw(_("Row {0}: Expense Entry Type must use a non-group Expense account in the Company currency.").format(row.idx))
			row.expense_entry_account = expense_type.account

		if not frappe.db.get_value("Mode of Payment", self.mode_of_payment, "enabled"):
			frappe.throw(_("Select an enabled Mode of Payment."))
		payment_account = frappe.db.get_value(
			"Mode of Payment Account",
			{"parent": self.mode_of_payment, "parenttype": "Mode of Payment", "company": self.company},
			"default_account",
		)
		if not payment_account:
			frappe.throw(_("Set a Default Account for this Company on the Mode of Payment."))
		credit = frappe.db.get_value(
			"Account", payment_account,
			["company", "root_type", "account_type", "is_group", "account_currency"], as_dict=True,
		)
		if (
			not credit or credit.company != self.company or credit.is_group
			or credit.root_type not in ("Asset", "Liability")
			or credit.account_type in ("Receivable", "Payable")
			or credit.account_currency != company_currency
		):
			frappe.throw(_("Mode of Payment must use a non-group Asset or Liability account in the Company currency."))
		return payment_account


def guard_journal_entry_cancel(doc, method=None):
	linked = frappe.db.get_value("Expense Entry", {"journal_entry": doc.name, "docstatus": 1}, "name")
	if linked:
		frappe.throw(_("Cancel Expense Entry {0} to reverse this Journal Entry.").format(linked))
