frappe.ui.form.on("Expense Entry", {
	setup(frm) {
		frm.set_query("expense_entry_type", "expenses", () => ({
			filters: { company: frm.doc.company, enabled: 1 },
		}));
		frm.set_query("mode_of_payment", () => ({ filters: { enabled: 1 } }));
		frm.set_query("cost_center", () => ({
			filters: { company: frm.doc.company, is_group: 0, disabled: 0 },
		}));
	},
	onload(frm) {
		if (frm.is_new() && frm.doc.company && !frm.doc.cost_center) {
			return set_default_cost_center(frm);
		}
	},
	company(frm) {
		frm.clear_table("expenses");
		frm.refresh_field("expenses");
		return set_default_cost_center(frm);
	},
});

async function set_default_cost_center(frm) {
	const company = frm.doc.company;
	const result = company
		? await frappe.db.get_value("Company", company, "cost_center")
		: null;
	if (frm.doc.company === company) {
		await frm.set_value("cost_center", result?.message?.cost_center || "");
	}
}
