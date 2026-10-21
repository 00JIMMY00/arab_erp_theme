frappe.ui.form.on("Expense Entry Type", {
	setup(frm) {
		frm.set_query("account", () => ({
			filters: { company: frm.doc.company, root_type: "Expense", is_group: 0 },
		}));
	},
	company(frm) {
		frm.set_value("account", null);
	},
});
