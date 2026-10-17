# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

# Data for the Project Dashboard page. Plain functions; the client reaches them through
# pm_agile/api/v1/project_dashboard.py.

import frappe
from frappe import _
from frappe.utils import today

LAST_PROJECT_KEY = "pm_dashboard_project"

# "done" counts towards a sprint's done/total; "excluded" rows are never counted;
# "end_field" decides overdue (end date passed and not done).
WORK_ITEM_RULES = {
	"Task": {
		"done": ("Completed", "Cancelled"),
		"excluded": ("Template",),
		"end_field": "exp_end_date",
	},
	"Issue": {
		"done": ("Resolved", "Closed"),
		"excluded": (),
		"end_field": "planned_end_date",
	},
}


def get_dashboard_data(project: str) -> dict:
	"""
	Collect the Project Dashboard payload in a handful of grouped queries.

	Parameters:
		project (str, required): Project name; the user must be able to read it.

	Returns:
		dict: {"project", "sprints", "backlog", "work_items"} as documented on the API endpoint.
	"""
	__check_project_access(project)

	work_items = {doctype: WorkItemCounts(doctype, project) for doctype in WORK_ITEM_RULES}
	return {
		"project": __get_project_header(project),
		"sprints": __get_sprints(project, work_items),
		"backlog": {doctype: counts.for_sprint(None) for doctype, counts in work_items.items()},
		"work_items": {doctype: counts.summary() for doctype, counts in work_items.items()},
	}


def remember_dashboard_project(project: str) -> None:
	"""
	Store the project as the user's default for the dashboard.

	Parameters:
		project (str, required): Project name; the user must be able to read it.

	Returns:
		None
	"""
	__check_project_access(project)
	frappe.defaults.set_user_default(LAST_PROJECT_KEY, project)


class WorkItemCounts:
	"""Task or Issue counts for one project, grouped by sprint and status in a single query."""

	def __init__(self, doctype: str, project: str):
		"""
		Run the grouped count query once (when the user can read the doctype) and index it by sprint.

		Parameters:
			doctype (str, required): "Task" or "Issue"; a key of WORK_ITEM_RULES.
			project (str, required): Project name.
		"""
		self.doctype = doctype
		self.project = project
		self.rules = WORK_ITEM_RULES[doctype]
		self.readable = bool(frappe.has_permission(doctype, "read"))
		self.rows = self.__count_by_sprint_and_status() if self.readable else []
		self.by_sprint = self.__done_and_total_by_sprint()

	def for_sprint(self, sprint: str | None) -> dict | None:
		"""
		Done and total counts for one sprint; None means the backlog (no sprint set).

		Parameters:
			sprint (str | None, required): Sprint name, or None for the backlog.

		Returns:
			dict | None: {"done": int, "total": int}, or None when the user cannot read this doctype.
		"""
		if not self.readable:
			return None

		return self.by_sprint.get(sprint, {"done": 0, "total": 0})

	def summary(self) -> dict:
		"""
		Totals for the Tasks / Issues section: total, overdue, and one entry per status in form order.

		Returns:
			dict: {"readable", "total", "overdue", "done_statuses", "excluded_statuses", "end_field",
			"by_status"};
			only {"readable": False} when the user cannot read this doctype.
		"""
		if not self.readable:
			return {"readable": False}

		by_status = dict.fromkeys(self.__status_options(), 0)
		for row in self.rows:
			by_status[row.status] = by_status.get(row.status, 0) + row.count

		return {
			"readable": True,
			"total": sum(by_status.values()),
			"overdue": self.__count_overdue(),
			"done_statuses": list(self.rules["done"]),
			"excluded_statuses": list(self.rules["excluded"]),
			"end_field": self.rules["end_field"],
			"by_status": [{"status": status, "count": count} for status, count in by_status.items()],
		}

	def __done_and_total_by_sprint(self) -> dict:
		"""
		Fold the grouped rows into done/total per sprint; the backlog is keyed by None.

		Returns:
			dict: {sprint name | None: {"done": int, "total": int}}
		"""
		by_sprint = {}
		for row in self.rows:
			counts = by_sprint.setdefault(row.sprint or None, {"done": 0, "total": 0})
			counts["total"] += row.count
			if row.status in self.rules["done"]:
				counts["done"] += row.count
		return by_sprint

	def __count_by_sprint_and_status(self) -> list:
		"""
		One grouped, permission-aware query for all counts of this doctype in the project.

		Returns:
			list: Rows of {"sprint", "status", "count"}.
		"""
		return frappe.get_list(
			self.doctype,
			filters=self.__base_filters(),
			fields=["sprint", "status", "count(name) as count"],
			group_by="sprint, status",
			order_by="sprint asc",
			limit_page_length=0,
		)

	def __count_overdue(self) -> int:
		"""
		Count items whose end date has passed and that are not done.

		Returns:
			int: Overdue item count.
		"""
		filters = [
			*self.__base_filters(),
			[self.rules["end_field"], "<", today()],
			["status", "not in", self.rules["done"]],
		]
		rows = frappe.get_list(self.doctype, filters=filters, fields=["count(name) as count"], order_by=None)
		return rows[0].count if rows else 0

	def __base_filters(self) -> list:
		"""
		Filters shared by every count: this project, minus excluded statuses.

		Returns:
			list: Frappe filter list.
		"""
		filters = [["project", "=", self.project]]
		if self.rules["excluded"]:
			filters.append(["status", "not in", self.rules["excluded"]])
		return filters

	def __status_options(self) -> list:
		"""
		The doctype's status options in form order, minus excluded ones, so zero counts still show.

		Returns:
			list: Status labels.
		"""
		options = frappe.get_meta(self.doctype).get_options("status").split("\n")
		return [status for status in options if status and status not in self.rules["excluded"]]


def __check_project_access(project: str) -> None:
	"""
	Throw unless `project` is a string naming a Project the user can read.

	Parameters:
		project (str, required): Project name from the client.

	Returns:
		None
	"""
	if not isinstance(project, str) or not project:
		frappe.throw(_("Project is required."), frappe.ValidationError, title=_("Missing Project"))

	if not frappe.db.exists("Project", project):
		frappe.throw(_("Project {0} not found.").format(project), frappe.DoesNotExistError)

	if not frappe.has_permission("Project", "read", project):
		frappe.throw(_("You cannot read Project {0}.").format(project), frappe.PermissionError)


def __get_project_header(project: str) -> dict:
	"""
	Fields shown in the dashboard's header strip.

	Parameters:
		project (str, required): Project name (access already checked).

	Returns:
		dict: name, project_name, status, expected_start_date, expected_end_date, percent_complete.
	"""
	return frappe.db.get_value(
		"Project",
		project,
		["name", "project_name", "status", "expected_start_date", "expected_end_date", "percent_complete"],
		as_dict=True,
	)


def __get_sprints(project: str, work_items: dict) -> list | None:
	"""
	The project's sprints, newest first, each with done/total counts per work item doctype.

	Parameters:
		project (str, required): Project name.
		work_items (dict, required): {doctype: WorkItemCounts} for the same project.

	Returns:
		list | None: Sprint dicts with a "counts" key, or None when the user cannot read Sprint.
	"""
	if not frappe.has_permission("Sprint", "read"):
		return None

	sprints = frappe.get_list(
		"Sprint",
		filters={"project": project},
		fields=["name", "sprint_name", "status", "start_date", "end_date", "goal"],
		order_by="start_date desc, creation desc",
		limit_page_length=0,
	)
	for sprint in sprints:
		sprint["counts"] = {doctype: counts.for_sprint(sprint.name) for doctype, counts in work_items.items()}
	return sprints
