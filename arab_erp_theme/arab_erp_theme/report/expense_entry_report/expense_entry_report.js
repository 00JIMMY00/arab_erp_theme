frappe.query_reports["Expense Entry Report"] = {
	filters: [
		{ fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company",
			default: frappe.defaults.get_user_default("Company") },
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date" },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date" },
		{ fieldname: "cost_center", label: __("Cost Center"), fieldtype: "Link", options: "Cost Center",
			get_query: () => ({ filters: expense_report_company_filters({ is_group: 0 }) }) },
		{ fieldname: "expense_entry_type", label: __("Expense Entry Type"), fieldtype: "Link", options: "Expense Entry Type",
			get_query: () => ({ filters: expense_report_company_filters() }) },
		{ fieldname: "expense_entry_account", label: __("Expense Entry Account"), fieldtype: "Link", options: "Account",
			get_query: () => ({ filters: expense_report_company_filters({ root_type: "Expense", is_group: 0 }) }) },
		{ fieldname: "mode_of_payment", label: __("Mode of Payment"), fieldtype: "Link", options: "Mode of Payment" },
		{ fieldname: "group_by", label: __("Group By"), fieldtype: "Select",
			options: ["", "Company", "Cost Center", "Expense Entry Type", "Expense Entry Account", "Mode of Payment", "Posting Date"] },
	],
	formatter(value, row, column, data, default_formatter) {
		if (data?.is_total_row) {
			const formatted = ["expense_entry", "group_value"].includes(column.fieldname)
				? frappe.utils.escape_html(value || "")
				: default_formatter(value, row, column, data);
			return `<strong>${formatted}</strong>`;
		}
		return default_formatter(value, row, column, data);
	},
};

function expense_report_company_filters(filters = {}) {
	const company = frappe.query_report.get_filter_value("company");
	return company ? { ...filters, company } : filters;
}
