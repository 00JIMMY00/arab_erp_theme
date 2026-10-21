frappe.ui.form.on("Expense Entry", {
	setup(frm) {
		frm.set_query("expense_entry_type", "expenses", () => ({
			filters: { company: frm.doc.company, enabled: 1 },
		}));
		frm.set_query("mode_of_payment", () => ({ filters: { enabled: 1 } }));
	},
	company(frm) {
		frm.clear_table("expenses");
		frm.refresh_field("expenses");
	},
});
