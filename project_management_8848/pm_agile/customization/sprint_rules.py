# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html, format_date, getdate

from project_management_8848.pm_agile.doctype.sprint.sprint_utils import throw_if_project_not_open

# Task statuses only allowed while the linked sprint is Active.
SPRINT_ACTIVE_ONLY_STATUSES = ("Working",)

# Sprint field -> field on the linked document. Every target is filled only when empty;
# `project` must then match the sprint's project. The document's `sprint` field holds the
# Sprint name. Keep in sync with pm.SPRINT_FIELD_MAP in public/js/pm_quick_create.js.
SPRINT_FIELD_MAP = {
	"Task": {
		"project": "project",
		"start_date": "exp_start_date",
		"end_date": "exp_end_date",
	},
	"Issue": {
		"project": "project",
		"start_date": "planned_start_date",
		"end_date": "planned_end_date",
	},
}


def fill_from_sprint(doc: Document) -> None:
	"""
	Copy the sprint's project and dates into empty fields of a Task or Issue.
	Runs in before_validate so ERPNext's own Task date checks see the filled values.

	Parameters:
		doc (Document, required): The Task or Issue being saved.

	Returns:
		None
	"""
	SprintLink(doc).fill_empty_fields()


def validate_sprint_link(doc: Document) -> None:
	"""
	Throw if the linked sprint belongs to another project, is Completed or in a project that is not
	Open and newly set on this save, is not Active while a Task moves to Working, or the document's dates fall outside the sprint.

	Parameters:
		doc (Document, required): The Task or Issue being saved.

	Returns:
		None
	"""
	SprintLink(doc).validate()


class SprintLink:
	"""The link between one Task or Issue and its Sprint, with the rules that keep the two consistent."""

	def __init__(self, doc: Document):
		"""
		Bind the rules to one document and pick its field map.

		Parameters:
			doc (Document, required): A Task or Issue; its doctype must be a key of SPRINT_FIELD_MAP.
		"""
		self.doc = doc
		self.field_map = SPRINT_FIELD_MAP[doc.doctype]

	def fill_empty_fields(self) -> None:
		"""
		Set each mapped field that is empty on the document from the sprint. Fields with a value are kept.

		Returns:
			None
		"""
		sprint = self.__get_sprint()
		if not sprint:
			return

		for sprint_field, doc_field in self.field_map.items():
			if not self.doc.get(doc_field):
				self.doc.set(doc_field, sprint.get(sprint_field))

	def validate(self) -> None:
		"""
		Enforce same project, no newly added items in a Completed sprint or a project that is not
		Open, Working only in an Active sprint, and dates within the sprint's range.

		Returns:
			None
		"""
		sprint = self.__get_sprint()
		if not sprint:
			return

		self.__validate_same_project(sprint)
		self.__validate_sprint_open(sprint)
		self.__validate_project_open(sprint)
		self.__validate_status_for_sprint(sprint)
		self.__validate_dates_within_sprint(sprint)

	def __validate_same_project(self, sprint: dict) -> None:
		"""
		Throw when the document's project differs from the sprint's project.

		Parameters:
			sprint (dict, required): Sprint row with `name` and `project`.

		Returns:
			None
		"""
		doc_project = self.doc.get(self.field_map["project"])
		if doc_project == sprint.project:
			return

		frappe.throw(
			_("Sprint {0} belongs to a different project: {1}, not {2}.").format(
				frappe.bold(escape_html(sprint.name)),
				frappe.bold(escape_html(sprint.project)),
				frappe.bold(escape_html(doc_project or _("(none)"))),
			),
			title=_("Sprint Project Mismatch"),
		)

	def __validate_sprint_open(self, sprint: dict) -> None:
		"""
		Throw when the sprint is Completed and was set or changed on this save.
		Items already in the sprint can still be edited after it completes.

		Parameters:
			sprint (dict, required): Sprint row with `name` and `status`.

		Returns:
			None
		"""
		if sprint.status != "Completed" or not self.doc.has_value_changed("sprint"):
			return

		frappe.throw(
			_("Sprint {0} is Completed. New {1} items cannot be added to it.").format(
				frappe.bold(escape_html(sprint.name)), _(self.doc.doctype)
			),
			title=_("Sprint Completed"),
		)

	def __validate_project_open(self, sprint: dict) -> None:
		"""
		Throw when the sprint was set or changed on this save and its project is not Open.
		Items already in the sprint can still be edited after the project closes.

		Parameters:
			sprint (dict, required): Sprint row with `project`.

		Returns:
			None
		"""
		if not self.doc.has_value_changed("sprint"):
			return

		throw_if_project_not_open(sprint.project, _("{0} items").format(_(self.doc.doctype)))

	def __validate_status_for_sprint(self, sprint: dict) -> None:
		"""
		Throw when a Task is moved to Working, or a Working Task is moved into a sprint, while
		the sprint is Planned or Completed. A Task already Working stays editable if its sprint
		later completes.

		Parameters:
			sprint (dict, required): Sprint row with `name` and `status`.

		Returns:
			None
		"""
		if self.doc.doctype != "Task" or self.doc.get("status") not in SPRINT_ACTIVE_ONLY_STATUSES:
			return

		if sprint.status == "Active":
			return

		if not (self.doc.has_value_changed("status") or self.doc.has_value_changed("sprint")):
			return

		frappe.throw(
			_("Task cannot be set to {0} because Sprint {1} is {2}. Activate the sprint first.").format(
				frappe.bold(_(self.doc.status)),
				frappe.bold(escape_html(sprint.name)),
				frappe.bold(_(sprint.status)),
			),
			title=_("Sprint Not Active"),
		)

	def __validate_dates_within_sprint(self, sprint: dict) -> None:
		"""
		Throw when the document's start or end date falls outside the sprint's date range.
		Checked on every save, including after the sprint's dates are moved.

		Parameters:
			sprint (dict, required): Sprint row with `name`, `start_date` and `end_date`.

		Returns:
			None
		"""
		sprint_start, sprint_end = getdate(sprint.start_date), getdate(sprint.end_date)
		for field in (self.field_map["start_date"], self.field_map["end_date"]):
			value = self.doc.get(field)
			if not value or sprint_start <= getdate(value) <= sprint_end:
				continue

			frappe.throw(
				_("{0} {1} must be within Sprint {2} dates: {3} to {4}.").format(
					_(self.doc.meta.get_label(field)),
					frappe.bold(format_date(value)),
					frappe.bold(escape_html(sprint.name)),
					format_date(sprint.start_date),
					format_date(sprint.end_date),
				),
				title=_("Date Outside Sprint"),
			)

	def __get_sprint(self) -> dict | None:
		"""
		Fetch the linked sprint, or None when the rules do not apply (no sprint, or a Task template).
		An unknown sprint name also returns None; Frappe's link validation reports it.

		Returns:
			dict | None: Sprint row with name, project, status, start_date, end_date.
		"""
		if not self.doc.get("sprint") or self.__is_task_template():
			return None

		return frappe.db.get_value(
			"Sprint",
			self.doc.sprint,
			["name", "project", "status", "start_date", "end_date"],
			as_dict=True,
		)

	def __is_task_template(self) -> bool:
		"""
		Task templates are copied into projects later, so they are never bound to a sprint.

		Returns:
			bool: True for a Task with status "Template" or the is_template flag set.
		"""
		if self.doc.doctype != "Task":
			return False

		return self.doc.get("status") == "Template" or bool(self.doc.get("is_template"))
