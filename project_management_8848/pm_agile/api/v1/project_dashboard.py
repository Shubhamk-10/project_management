# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe

from project_management_8848.pm_agile.page.pm_projects.pm_projects import (
	get_dashboard_data,
	remember_dashboard_project,
)
from project_management_8848.utils.api_handlers.response_formatter import api_error, api_response


@frappe.whitelist(methods=["GET"])
def get_dashboard(project: str):
	"""
	Return everything the Project Dashboard page renders for one project: header, sprints with
	done/total Task and Issue counts, backlog counts, and Task/Issue counts by status.
	Counts respect the caller's permissions.

	**Endpoint:** `/api/method/project_management_8848.pm_agile.api.v1.project_dashboard.get_dashboard`
	**HTTP Method:** GET
	**Parameters:**
		- project (str, required): Project name (ID)
	**Response:**
	```json
	{
		"status": true,
		"status_code": 200,
		"message": "Dashboard loaded",
		"data": {
			"project": {"name": "PROJ-0001", "project_name": "Website", "status": "Open",
				"expected_start_date": "2026-11-01", "expected_end_date": "2026-12-31",
				"percent_complete": 40.0},
			"sprints": [{"name": "PROJ-0001-SPR-01", "sprint_name": "Sprint 1", "status": "Active",
				"start_date": "2026-11-01", "end_date": "2026-11-14", "goal": "Checkout flow",
				"counts": {"Task": {"done": 2, "total": 5}, "Issue": {"done": 0, "total": 1}}}],
			"backlog": {"Task": {"done": 0, "total": 3}, "Issue": {"done": 1, "total": 2}},
			"work_items": {
				"Task": {"readable": true, "total": 8, "overdue": 1, "done_statuses": ["Completed", "Cancelled"],
					"excluded_statuses": ["Template"], "end_field": "exp_end_date", "by_status": [{"status": "Open", "count": 4}]},
				"Issue": {"readable": false}
			}
		},
		"errors": null
	}
	```
	Failure (403 no access, 404 unknown project, 400 missing project):
	```json
	{"status": false, "status_code": 403, "message": "...", "data": null,
		"errors": {"type": "PermissionError"}}
	```
	"""
	try:
		data = get_dashboard_data(project)
	except frappe.ValidationError as exc:
		return api_error(exc)

	return api_response(message="Dashboard loaded", data=data)


@frappe.whitelist(methods=["POST"])
def set_dashboard_project(project: str):
	"""
	Remember the project last opened on the Project Dashboard for the current user, so the page
	reopens on it next time.

	**Endpoint:** `/api/method/project_management_8848.pm_agile.api.v1.project_dashboard.set_dashboard_project`
	**HTTP Method:** POST
	**Parameters:**
		- project (str, required): Project name (ID); the user must be able to read it
	**Response:**
	```json
	{"status": true, "status_code": 200, "message": "Project remembered",
		"data": {"project": "PROJ-0001"}, "errors": null}
	```
	"""
	try:
		remember_dashboard_project(project)
	except frappe.ValidationError as exc:
		return api_error(exc)

	return api_response(message="Project remembered", data={"project": project})
