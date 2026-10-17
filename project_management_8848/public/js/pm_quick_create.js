// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

// Shared create helpers for the Sprint form, the Project Dashboard and sprint_filter.js.
// Loaded on every desk page through app_include_js.

frappe.provide("pm");

// Sprint field -> field on the new or linked document. `sprint` itself takes the Sprint name.
// Keep in sync with SPRINT_FIELD_MAP in pm_agile/customization/sprint_rules.py.
pm.SPRINT_FIELD_MAP = {
	Task: {
		project: "project",
		start_date: "exp_start_date",
		end_date: "exp_end_date",
	},
	Issue: {
		project: "project",
		start_date: "planned_start_date",
		end_date: "planned_end_date",
	},
};

/**
 * Fetch the sprint fields the create helpers need.
 *
 * @param {string} name - Sprint name.
 * @returns {Promise<object|undefined>} {name, project, status, start_date, end_date}, or undefined if not readable.
 */
pm.get_sprint = function (name) {
	return frappe.db
		.get_value("Sprint", name, ["name", "project", "status", "start_date", "end_date"])
		.then((r) => (r.message && r.message.name ? r.message : undefined));
};

/**
 * Build the values a new Task or Issue takes from a sprint.
 *
 * @param {string} doctype - "Task" or "Issue".
 * @param {object} sprint - Sprint row from pm.get_sprint.
 * @returns {object} {sprint, project, <start field>, <end field>}
 */
pm.map_from_sprint = function (doctype, sprint) {
	const values = { sprint: sprint.name };
	for (const [sprint_field, doc_field] of Object.entries(pm.SPRINT_FIELD_MAP[doctype])) {
		values[doc_field] = sprint[sprint_field];
	}
	return values;
};

/**
 * Open a new Task or Issue pre-filled from a sprint. Completed sprints are refused.
 *
 * @param {string} doctype - "Task" or "Issue".
 * @param {string} sprint_name - Sprint name.
 * @returns {Promise<void>}
 */
pm.new_from_sprint = function (doctype, sprint_name) {
	return pm.get_sprint(sprint_name).then((sprint) => {
		if (!sprint) {
			frappe.msgprint(
				__("Sprint {0} was not found or you cannot read it.", [
					frappe.utils.escape_html(sprint_name),
				])
			);
			return;
		}
		if (sprint.status === "Completed") {
			frappe.msgprint({
				title: __("Sprint Completed"),
				message: __("Sprint {0} is Completed. New items cannot be added to it.", [
					frappe.utils.escape_html(sprint.name).bold(),
				]),
				indicator: "orange",
			});
			return;
		}
		return frappe.new_doc(doctype, pm.map_from_sprint(doctype, sprint));
	});
};

/**
 * Ask for an optional open sprint of the project, then open a new Task or Issue.
 * Without a sprint the item goes to the project backlog.
 *
 * @param {string} doctype - "Task" or "Issue".
 * @param {string} project - Project name; required.
 * @returns {void}
 */
pm.new_for_project = function (doctype, project) {
	if (!project) {
		frappe.msgprint(__("Select a Project first."));
		return;
	}

	const dialog = new frappe.ui.Dialog({
		title: __("New {0}", [__(doctype)]),
		fields: [
			{
				fieldname: "project",
				fieldtype: "Link",
				label: __("Project"),
				options: "Project",
				default: project,
				read_only: 1,
			},
			{
				fieldname: "sprint",
				fieldtype: "Link",
				label: __("Sprint"),
				options: "Sprint",
				description: __("Leave empty to add the item to the project backlog."),
				get_query: () => pm.open_sprint_query(project),
			},
		],
		primary_action_label: __("Create"),
		primary_action({ sprint }) {
			dialog.hide();
			if (sprint) {
				pm.new_from_sprint(doctype, sprint);
			} else {
				frappe.new_doc(doctype, { project });
			}
		},
	});
	dialog.show();
};

/**
 * Open a new Sprint for the project.
 *
 * @param {string} project - Project name.
 * @returns {Promise<void>}
 */
pm.new_sprint = function (project) {
	return frappe.new_doc("Sprint", { project });
};

/**
 * Link-field query for sprints that can still take items.
 *
 * @param {string} [project] - Restrict to this project when given.
 * @returns {object} {filters} for a Link field's get_query / set_query.
 */
pm.open_sprint_query = function (project) {
	const filters = { status: ["!=", "Completed"] };
	if (project) filters.project = project;
	return { filters };
};
