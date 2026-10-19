# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe.model.document import Document


def make_project(project_name: str | None = None) -> Document:
	"""
	Insert a Project for a test. Names are random so tests do not depend on each other.

	Parameters:
		project_name (str, optional): Project name; a random one is used when omitted.

	Returns:
		Document: The inserted Project.
	"""
	return frappe.get_doc(
		{"doctype": "Project", "project_name": project_name or f"PM Test {frappe.generate_hash(length=8)}"}
	).insert()


def close_project(project: str, status: str) -> None:
	"""
	Set a Project's status directly, skipping ERPNext's Project hooks so only the status changes.

	Parameters:
		project (str, required): Project name.
		status (str, required): "Completed" or "Cancelled".

	Returns:
		None
	"""
	frappe.db.set_value("Project", project, "status", status)


def make_sprint(
	project: str,
	start_date: str = "2026-11-01",
	end_date: str = "2026-11-14",
	status: str = "Planned",
) -> Document:
	"""
	Insert a Sprint for a test.

	Parameters:
		project (str, required): Project name.
		start_date (str, optional): ISO start date. Default 2026-11-01.
		end_date (str, optional): ISO end date. Default 2026-11-14.
		status (str, optional): Planned, Active or Completed. Default Planned.

	Returns:
		Document: The inserted Sprint.
	"""
	return frappe.get_doc(
		{
			"doctype": "Sprint",
			"sprint_name": f"Sprint {frappe.generate_hash(length=6)}",
			"project": project,
			"status": status,
			"start_date": start_date,
			"end_date": end_date,
		}
	).insert()


def make_work_item(doctype: str, **values) -> Document:
	"""
	Insert a Task or Issue with a random subject plus the given field values.

	Parameters:
		doctype (str, required): "Task" or "Issue".
		**values: Field values, e.g. sprint="P-SPR-01".

	Returns:
		Document: The inserted document.
	"""
	return frappe.get_doc(
		{"doctype": doctype, "subject": f"PM Test {frappe.generate_hash(length=8)}", **values}
	).insert()
