// Copyright (c) 2026 8848 Digital LLP. All rights reserved.
// Proprietary and confidential. Unauthorized copying, distribution, or use
// of this file, via any medium, is strictly prohibited without prior
// written permission from 8848 Digital LLP.

// HTML builders for the Project Dashboard (pm_agile/page/pm_projects), loaded by it with frappe.require.
// Every value from the server passes through pm.escape() before it reaches the DOM.

frappe.provide("pm");

pm.ProjectDashboardView = class ProjectDashboardView {
	/**
	 * @param {object} data - `data` from the get_dashboard API.
	 */
	constructor(data) {
		this.data = data;
	}

	/**
	 * Header strip: project name, status, expected dates and % complete.
	 *
	 * @returns {string} HTML.
	 */
	header() {
		const project = this.data.project;
		const percent = Math.round(flt(project.percent_complete));
		const title = project.project_name || project.name;
		return `<div class="pm-header">
			<span class="pm-header-title">${pm.escape(title)}</span>
			${this.pill(project.status)}
			<span class="pm-muted">${this.date_range(
				project.expected_start_date,
				project.expected_end_date
			)}</span>
			<div class="pm-progress">
				<span class="pm-muted">${pm.escape(__("{0}% complete", [percent]))}</span>
				<div class="pm-progress-bar"><span style="width: ${percent}%"></span></div>
			</div>
		</div>`;
	}

	/**
	 * Sprints section: one card per sprint (newest first) plus the Backlog card.
	 *
	 * @returns {string} HTML.
	 */
	sprints_section() {
		const sprints = this.data.sprints;
		if (sprints === null) return this.section(__("Sprints"), this.no_access("Sprint"));

		const cards = sprints.map((sprint) => this.sprint_card(sprint));
		cards.push(this.backlog_card());
		return this.section(
			__("Sprints"),
			`<div class="pm-grid">${cards.join("")}</div>`,
			sprints.length
		);
	}

	/**
	 * Tasks or Issues section: total, overdue and one card per status.
	 *
	 * @param {string} doctype - "Task" or "Issue".
	 * @returns {string} HTML.
	 */
	work_section(doctype) {
		const title = doctype === "Task" ? __("Tasks") : __("Issues");
		const summary = this.data.work_items[doctype];
		if (!summary.readable) return this.section(title, this.no_access(doctype));

		const overdue_filters = {
			[summary.end_field]: ["<", frappe.datetime.get_today()],
			status: ["not in", summary.done_statuses],
		};
		const cards = [
			this.stat_card(doctype, __("Total"), summary.total, {}),
			this.stat_card(doctype, __("Overdue"), summary.overdue, overdue_filters, "pm-overdue"),
			...summary.by_status.map((row) =>
				this.stat_card(doctype, __(row.status), row.count, { status: row.status })
			),
		];
		return this.section(
			title,
			`<div class="pm-grid pm-stats">${cards.join("")}</div>`,
			summary.total
		);
	}

	/**
	 * One sprint card with counts and actions. Completed sprints get no "+" buttons.
	 *
	 * @param {object} sprint - Sprint row with `counts`.
	 * @returns {string} HTML.
	 */
	sprint_card(sprint) {
		const filters = { sprint: sprint.name };
		const add_buttons =
			sprint.status === "Completed"
				? ""
				: this.button("new-in-sprint", __("+ Task"), {
						doctype: "Task",
						sprint: sprint.name,
				  }) +
				  this.button("new-in-sprint", __("+ Issue"), {
						doctype: "Issue",
						sprint: sprint.name,
				  });
		const goal = sprint.goal ? `<div class="pm-goal">${pm.escape(sprint.goal)}</div>` : "";

		return `<div class="pm-card">
			<div class="pm-card-head">
				<span class="pm-card-title" title="${pm.escape(sprint.name)}">${pm.escape(
			sprint.sprint_name
		)}</span>
				${this.pill(sprint.status)}
			</div>
			<div class="pm-muted">${this.date_range(sprint.start_date, sprint.end_date)}</div>
			${goal}
			<div class="pm-counts">
				${this.count_link("Task", sprint.counts.Task, filters)}
				${this.count_link("Issue", sprint.counts.Issue, filters)}
			</div>
			<div class="pm-card-actions">
				${add_buttons}
				${this.button("open-sprint", __("Open"), { sprint: sprint.name })}
			</div>
		</div>`;
	}

	/**
	 * Backlog card: project items with no sprint.
	 *
	 * @returns {string} HTML.
	 */
	backlog_card() {
		const filters = { sprint: ["is", "not set"] };
		return `<div class="pm-card pm-backlog">
			<div class="pm-card-head"><span class="pm-card-title">${pm.escape(__("Backlog"))}</span></div>
			<div class="pm-muted">${pm.escape(__("Items not planned into a sprint"))}</div>
			<div class="pm-counts">
				${this.count_link("Task", this.data.backlog.Task, filters)}
				${this.count_link("Issue", this.data.backlog.Issue, filters)}
			</div>
		</div>`;
	}

	/**
	 * Clickable "Tasks 2/5" link opening the filtered list; a dash when the doctype is not readable.
	 *
	 * @param {string} doctype - "Task" or "Issue".
	 * @param {object|null} counts - {done, total}, or null without read access.
	 * @param {object} filters - Route filters for the list.
	 * @returns {string} HTML.
	 */
	count_link(doctype, counts, filters) {
		const label = doctype === "Task" ? __("Tasks") : __("Issues");
		if (!counts) return `<span class="pm-muted">${pm.escape(label)}: -</span>`;

		return `<span class="pm-link" data-action="list" data-doctype="${pm.escape(doctype)}"
			data-filters="${pm.escape(JSON.stringify(filters))}">
			${pm.escape(label)} ${counts.done}/${counts.total}</span>`;
	}

	/**
	 * Number card opening the list with the given filters.
	 *
	 * @param {string} doctype - "Task" or "Issue".
	 * @param {string} label - Card label (already translated).
	 * @param {number} value - Count to show.
	 * @param {object} filters - Route filters for the list.
	 * @param {string} [extra_class] - Additional CSS class.
	 * @returns {string} HTML.
	 */
	stat_card(doctype, label, value, filters, extra_class = "") {
		return `<div class="pm-card pm-stat ${extra_class}" data-action="list" data-doctype="${pm.escape(
			doctype
		)}"
			data-filters="${pm.escape(JSON.stringify(filters))}">
			<span class="pm-muted">${pm.escape(label)}</span>
			<span class="pm-stat-value">${cint(value)}</span>
		</div>`;
	}

	/**
	 * Section wrapper with a title and optional count.
	 *
	 * @param {string} title - Section title (already translated).
	 * @param {string} body - Inner HTML.
	 * @param {number} [count] - Shown next to the title when given.
	 * @returns {string} HTML.
	 */
	section(title, body, count) {
		const badge = count === undefined ? "" : `<span class="pm-muted">${cint(count)}</span>`;
		return `<div class="pm-section">
			<div class="pm-section-title">${pm.escape(title)} ${badge}</div>
			${body}
		</div>`;
	}

	/**
	 * Small button wired through data-action.
	 *
	 * @param {string} action - data-action value.
	 * @param {string} label - Button label (already translated).
	 * @param {object} attrs - Extra data-* attributes, e.g. {doctype, sprint}.
	 * @returns {string} HTML.
	 */
	button(action, label, attrs) {
		const data_attrs = Object.entries(attrs)
			.map(([key, value]) => `data-${key}="${pm.escape(value)}"`)
			.join(" ");
		return `<button class="btn btn-xs btn-default" data-action="${action}" ${data_attrs}>${pm.escape(
			label
		)}</button>`;
	}

	/**
	 * Coloured status pill using Frappe's indicator classes.
	 *
	 * @param {string} status - Status value.
	 * @returns {string} HTML.
	 */
	pill(status) {
		if (!status) return "";
		const color = pm.ProjectDashboard.STATUS_COLORS[status] || "gray";
		return `<span class="indicator-pill ${color}">${pm.escape(__(status))}</span>`;
	}

	/**
	 * "1 Nov 2026 - 14 Nov 2026" in the user's date format.
	 *
	 * @param {string} start - ISO date or empty.
	 * @param {string} end - ISO date or empty.
	 * @returns {string} Escaped text.
	 */
	date_range(start, end) {
		if (!start && !end) return pm.escape(__("No dates"));
		const to_user = (date) => (date ? frappe.datetime.str_to_user(date) : "?");
		return pm.escape(`${to_user(start)} - ${to_user(end)}`);
	}

	/**
	 * Note shown in place of a section the user cannot read.
	 *
	 * @param {string} doctype - The unreadable doctype.
	 * @returns {string} HTML.
	 */
	no_access(doctype) {
		return `<div class="pm-empty">${pm.escape(
			__("You do not have access to {0}.", [__(doctype)])
		)}</div>`;
	}
};

/**
 * Escape a value for HTML text or a double-quoted attribute.
 *
 * @param {*} value - Any value; null and undefined become "".
 * @returns {string} Escaped string.
 */
pm.escape = function (value) {
	return frappe.utils.escape_html(value);
};
