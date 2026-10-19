# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html, format_date, getdate

# Project status a Sprint can be created in, and Tasks/Issues linked to its sprints.
OPEN_PROJECT_STATUS = "Open"


def validate_date_range(sprint: Document) -> None:
	"""
	Throw when the sprint ends before it starts. A one-day sprint (same start and end) is allowed.

	Parameters:
		sprint (Document, required): The Sprint being validated.

	Returns:
		None
	"""
	if getdate(sprint.end_date) >= getdate(sprint.start_date):
		return

	frappe.throw(
		_("End Date {0} cannot be before Start Date {1}.").format(
			format_date(sprint.end_date), format_date(sprint.start_date)
		),
		title=_("Invalid Sprint Dates"),
	)


def validate_single_active_sprint(sprint: Document) -> None:
	"""
	Throw when another sprint of the same project is already Active.

	Parameters:
		sprint (Document, required): The Sprint being validated.

	Returns:
		None
	"""
	if sprint.status != "Active":
		return

	active_sprint = frappe.db.get_value(
		"Sprint",
		{"project": sprint.project, "status": "Active", "name": ("!=", sprint.name)},
		"name",
	)
	if not active_sprint:
		return

	frappe.throw(
		_(
			"Sprint {0} is already Active for Project {1}. Complete it before activating another sprint."
		).format(frappe.bold(escape_html(active_sprint)), frappe.bold(escape_html(sprint.project))),
		title=_("Active Sprint Exists"),
	)


def validate_project_open(sprint: Document) -> None:
	"""
	Throw when a new sprint, or a sprint moved to another project, targets a project that is not Open.
	Existing sprints stay editable after their project is Completed or Cancelled.

	Parameters:
		sprint (Document, required): The Sprint being validated.

	Returns:
		None
	"""
	if not (sprint.is_new() or sprint.has_value_changed("project")):
		return

	throw_if_project_not_open(sprint.project, _("Sprints"))


def throw_if_project_not_open(project: str, items_label: str) -> None:
	"""
	Throw when the project's status is not Open.

	Parameters:
		project (str, required): Project name.
		items_label (str, required): Translated plural of what is being added, e.g. "Sprints".

	Returns:
		None
	"""
	status = frappe.db.get_value("Project", project, "status")
	if not status or status == OPEN_PROJECT_STATUS:
		return

	frappe.throw(
		_("Project {0} is {1}. New {2} can only be added to an Open project.").format(
			frappe.bold(escape_html(project)), frappe.bold(_(status)), items_label
		),
		title=_("Project Not Open"),
	)
