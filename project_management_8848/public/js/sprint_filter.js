// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

// Sprint field behaviour on the Task and Issue forms. Loaded through doctype_js for both,
// so the guard stops the handlers being registered twice when both forms are opened.
// The same rules run on the server (pm_agile/customization/sprint_rules.py).

frappe.provide("pm");

if (!pm.sprint_filter_registered) {
	pm.sprint_filter_registered = true;

	const sprint_handlers = {
		/**
		 * Offer only open sprints of the form's project in the Sprint field.
		 *
		 * @param {object} frm - The Task or Issue form.
		 * @returns {void}
		 */
		setup(frm) {
			frm.set_query("sprint", () => pm.open_sprint_query(frm.doc.project));
		},

		/**
		 * On picking a sprint, follow its project and fill empty date fields.
		 * Clearing the sprint moves the item to the backlog and keeps its dates.
		 *
		 * @param {object} frm - The Task or Issue form.
		 * @returns {Promise<void>|undefined}
		 */
		sprint(frm) {
			if (!frm.doc.sprint) return;

			return pm.get_sprint(frm.doc.sprint).then((sprint) => {
				if (!sprint || sprint.name !== frm.doc.sprint) return;
				return frm.set_value(pm.sprint_values_to_fill(frm, sprint));
			});
		},

		/**
		 * Clear the sprint when the project changes to one the sprint does not belong to.
		 *
		 * @param {object} frm - The Task or Issue form.
		 * @returns {Promise<void>|undefined}
		 */
		project(frm) {
			if (!frm.doc.sprint) return;

			return pm.get_sprint(frm.doc.sprint).then((sprint) => {
				if (sprint && sprint.project === frm.doc.project) return;
				return frm.set_value("sprint", "");
			});
		},
	};

	for (const doctype of Object.keys(pm.SPRINT_FIELD_MAP)) {
		frappe.ui.form.on(doctype, sprint_handlers);
	}
}

/**
 * Values to set on a form after a sprint is picked: the project always follows the sprint,
 * other mapped fields only when empty.
 *
 * @param {object} frm - The Task or Issue form.
 * @param {object} sprint - Sprint row from pm.get_sprint.
 * @returns {object} {fieldname: value} for frm.set_value.
 */
pm.sprint_values_to_fill = function (frm, sprint) {
	const mapped = pm.map_from_sprint(frm.doctype, sprint);
	const project_field = pm.SPRINT_FIELD_MAP[frm.doctype].project;
	const values = {};

	for (const [fieldname, value] of Object.entries(mapped)) {
		if (fieldname === "sprint") continue;
		if (fieldname === project_field || !frm.doc[fieldname]) values[fieldname] = value;
	}
	return values;
};
