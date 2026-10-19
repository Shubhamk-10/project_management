# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

# Sprint entries for the Connections tab of ERPNext forms. Used by the
# override_doctype_dashboards hooks in customization/<doctype>/<doctype>_dashboard.py.

from frappe import _


def add_sprints_to_project(data: dict) -> dict:
	"""
	List the Project's sprints first in ERPNext's "Project" group, or in a group of their own
	when that group is missing.

	Parameters:
		data (dict, required): ERPNext's Project dashboard config, linked through `project`.

	Returns:
		dict: The same config with Sprint added.
	"""
	for group in data.get("transactions", []):
		if group.get("label") == _("Project"):
			group["items"].insert(0, "Sprint")
			return data

	data.setdefault("transactions", []).insert(0, {"label": _("Sprint"), "items": ["Sprint"]})
	return data


def add_sprint_to_work_item(data: dict) -> dict:
	"""
	Show the sprint set in a Task's or Issue's `sprint` field as an internal link in its own group.

	Parameters:
		data (dict, required): ERPNext's Task or Issue dashboard config.

	Returns:
		dict: The same config with the Sprint internal link and group added.
	"""
	data.setdefault("internal_links", {})["Sprint"] = "sprint"
	data.setdefault("transactions", []).insert(0, {"label": _("Sprint"), "items": ["Sprint"]})
	return data
