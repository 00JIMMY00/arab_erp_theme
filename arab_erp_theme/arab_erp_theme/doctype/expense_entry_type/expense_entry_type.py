import frappe
from frappe import _
from frappe.model.document import Document


class ExpenseEntryType(Document):
	def validate(self):
		account = frappe.db.get_value(
			"Account", self.account, ["company", "root_type", "is_group", "account_currency"], as_dict=True
		)
		if not account or account.company != self.company or account.root_type != "Expense" or account.is_group:
			frappe.throw(_("Choose a non-group Expense account for the selected Company."))
		company_currency = frappe.db.get_value("Company", self.company, "default_currency")
		if account.account_currency != company_currency:
			frappe.throw(_("The Expense account must use the Company currency."))
