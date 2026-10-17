# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html, format_date, getdate


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
