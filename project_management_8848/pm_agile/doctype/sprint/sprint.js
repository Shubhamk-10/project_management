// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

frappe.ui.form.on("Sprint", {
	/**
	 * Add the Create > Task / Issue buttons once the sprint is saved and still open.
	 *
	 * @param {object} frm - The Sprint form.
	 * @returns {void}
	 */
	refresh(frm) {
		if (frm.is_new() || frm.doc.status === "Completed") return;

		const create_label = __("Create");
		for (const doctype of ["Task", "Issue"]) {
			frm.add_custom_button(
				__(doctype),
				() => pm.new_from_sprint(doctype, frm.doc.name),
				create_label
			);
		}
	},
});
