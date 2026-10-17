# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html

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
	Throw if the linked sprint belongs to another project, or is Completed and newly set on this save.

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
		Enforce same project and no newly added items in a Completed sprint.

		Returns:
			None
		"""
		sprint = self.__get_sprint()
		if not sprint:
			return

		self.__validate_same_project(sprint)
		self.__validate_sprint_open(sprint)

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
