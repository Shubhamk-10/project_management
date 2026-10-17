// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

// Project Dashboard: /app/pm-projects[/<project>]. Data comes from
// pm_agile/api/v1/project_dashboard.py; HTML comes from public/js/pm_projects_view.js;
// create actions use pm_quick_create.js.

frappe.pages["pm-projects"].on_page_load = function (wrapper) {
	wrapper.pm_dashboard = new pm.ProjectDashboard(wrapper);
};

frappe.pages["pm-projects"].on_page_show = function (wrapper) {
	wrapper.pm_dashboard.show_route_project();
};

frappe.provide("pm");

pm.ProjectDashboard = class ProjectDashboard {
	static API = "project_management_8848.pm_agile.api.v1.project_dashboard";
	static VIEW_ASSET = "/assets/project_management_8848/js/pm_projects_view.js";
	static LAST_PROJECT_KEY = "pm_dashboard_project";
	static STATUS_COLORS = {
		Planned: "gray",
		Active: "blue",
		Completed: "green",
		Cancelled: "gray",
		Open: "orange",
		Working: "blue",
		"Pending Review": "purple",
		Overdue: "red",
		Replied: "blue",
		"On Hold": "yellow",
		Resolved: "green",
		Closed: "gray",
	};

	/**
	 * Build the page shell, toolbar and click handling. Data loads on page show.
	 *
	 * @param {HTMLElement} wrapper - Page wrapper provided by Frappe.
	 */
	constructor(wrapper) {
		this.project = null;
		this.data = null;
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Project Dashboard"),
			single_column: true,
		});
		this.$body = $('<div class="pm-dashboard"></div>').appendTo(this.page.main);
		this.$body.on("click", "[data-action]", (event) =>
			this.handle_action($(event.currentTarget))
		);
		this.make_toolbar();
		this.render_empty();
	}

	/**
	 * Add the Project selector and the primary "New" button group.
	 *
	 * @returns {void}
	 */
	make_toolbar() {
		this.project_field = this.page.add_field({
			fieldname: "project",
			fieldtype: "Link",
			label: __("Project"),
			options: "Project",
			get_query: () => ({ filters: { status: "Open" } }),
			change: () => this.select_project(this.project_field.get_value()),
		});

		const group = __("New");
		this.page.add_inner_button(__("Sprint"), () => this.create("Sprint"), group);
		this.page.add_inner_button(__("Task"), () => this.create("Task"), group);
		this.page.add_inner_button(__("Issue"), () => this.create("Issue"), group);
		this.page.set_inner_btn_group_as_primary(group);
	}

	/**
	 * Open the project from the URL, else the user's last project. Re-showing the same
	 * project reloads it, so counts are fresh after creating items elsewhere.
	 *
	 * @returns {void}
	 */
	show_route_project() {
		const project =
			frappe.get_route()[1] ||
			frappe.defaults.get_user_default(pm.ProjectDashboard.LAST_PROJECT_KEY);
		if (project && project === this.project) {
			this.load();
		} else if (project) {
			this.select_project(project);
		}
	}

	/**
	 * Switch to a project: sync the selector and URL, remember it for the user, load data.
	 *
	 * @param {string} project - Project name; empty shows the empty state.
	 * @returns {void}
	 */
	select_project(project) {
		if (project === this.project) return;

		this.project = project || null;
		if (!this.project) {
			this.render_empty();
			return;
		}

		this.project_field.set_value(this.project);
		// Update the URL without re-routing, which would show the page (and load) again.
		window.history.replaceState(
			null,
			"",
			`/app/pm-projects/${encodeURIComponent(this.project)}`
		);
		frappe.defaults.set_user_default_local(pm.ProjectDashboard.LAST_PROJECT_KEY, this.project);
		frappe.call({
			method: `${pm.ProjectDashboard.API}.set_dashboard_project`,
			args: { project: this.project },
		});
		this.load();
	}

	/**
	 * Fetch dashboard data for the current project and render it. Late responses for a
	 * project the user already left are dropped.
	 *
	 * @returns {void}
	 */
	load() {
		const project = this.project;
		frappe.call({
			method: `${pm.ProjectDashboard.API}.get_dashboard`,
			type: "GET",
			args: { project },
			callback: (r) => {
				if (project !== this.project) return;
				this.data = r.message.data;
				this.render();
			},
			error: (xhr) => {
				if (project !== this.project) return;
				const message = xhr.responseJSON && xhr.responseJSON.message;
				this.render_empty(
					(message && message.message) || __("Could not load the dashboard.")
				);
			},
		});
	}

	/**
	 * Run a click on any element with data-action.
	 *
	 * @param {jQuery} $target - The clicked element.
	 * @returns {void}
	 */
	handle_action($target) {
		const { action, doctype, sprint } = $target.data();
		if (action === "list") this.open_list(doctype, $target.data("filters") || {});
		if (action === "new-in-sprint") pm.new_from_sprint(doctype, sprint);
		if (action === "open-sprint") frappe.set_route("Form", "Sprint", sprint);
		if (action === "new") this.create(doctype);
	}

	/**
	 * Create a Sprint, Task or Issue for the selected project.
	 *
	 * @param {string} doctype - "Sprint", "Task" or "Issue".
	 * @returns {void}
	 */
	create(doctype) {
		if (!this.project) {
			frappe.msgprint(__("Select a Project first."));
			return;
		}
		if (doctype === "Sprint") pm.new_sprint(this.project);
		else pm.new_for_project(doctype, this.project);
	}

	/**
	 * Open a list view filtered to the project, the given filters, and (for Task) no templates.
	 *
	 * @param {string} doctype - "Task" or "Issue".
	 * @param {object} filters - Extra route filters, e.g. {sprint: ["is", "not set"]}.
	 * @returns {void}
	 */
	open_list(doctype, filters) {
		const excluded = this.data.work_items[doctype].excluded_statuses || [];
		const route_options = { project: this.project };
		if (excluded.length) route_options.status = ["not in", excluded];
		frappe.route_options = Object.assign(route_options, filters);
		frappe.set_route("List", doctype);
	}

	/**
	 * Show the prompt to pick a project, or an error message.
	 *
	 * @param {string} [message] - Text to show instead of the default prompt.
	 * @returns {void}
	 */
	render_empty(message) {
		const text = message || __("Select a project to see its sprints, tasks and issues.");
		this.$body.html(`<div class="pm-empty">${frappe.utils.escape_html(text)}</div>`);
	}

	/**
	 * Render the header strip and the Sprints, Tasks and Issues sections from this.data.
	 * The view script loads on first render; frappe.require caches it afterwards.
	 *
	 * @returns {void}
	 */
	render() {
		const data = this.data;
		frappe.require(pm.ProjectDashboard.VIEW_ASSET, () => {
			if (data !== this.data) return;
			const view = new pm.ProjectDashboardView(data);
			this.$body.html(
				view.header() +
					view.sprints_section() +
					view.work_section("Task") +
					view.work_section("Issue")
			);
		});
	}
};
