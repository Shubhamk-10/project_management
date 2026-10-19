# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

from project_management_8848.tests.utils import (
	close_project,
	make_project,
	make_sprint,
	make_work_item,
)


class TestSprintRules(FrappeTestCase):
	"""Task/Issue doc_events: fill from sprint, same project, no new items in a Completed sprint,
	Working only in an Active sprint, dates within the sprint, sprint's project must be Open."""

	def test_task_with_only_sprint_gets_project_and_dates(self):
		"""A Task saved with just a sprint takes the sprint's project and date range."""
		project = make_project()
		sprint = make_sprint(project.name)

		task = make_work_item("Task", sprint=sprint.name)

		self.assertEqual(task.project, project.name)
		self.assertEqual(getdate(task.exp_start_date), getdate("2026-11-01"))
		self.assertEqual(getdate(task.exp_end_date), getdate("2026-11-14"))

	def test_existing_dates_are_kept(self):
		"""Dates the user entered win over the sprint's dates."""
		project = make_project()
		sprint = make_sprint(project.name)

		task = make_work_item(
			"Task", sprint=sprint.name, exp_start_date="2026-11-03", exp_end_date="2026-11-05"
		)

		self.assertEqual(getdate(task.exp_start_date), getdate("2026-11-03"))
		self.assertEqual(getdate(task.exp_end_date), getdate("2026-11-05"))

	def test_issue_gets_planned_dates(self):
		"""An Issue fills project and the custom planned date fields."""
		project = make_project()
		sprint = make_sprint(project.name)

		issue = make_work_item("Issue", sprint=sprint.name)

		self.assertEqual(issue.project, project.name)
		self.assertEqual(getdate(issue.planned_start_date), getdate("2026-11-01"))
		self.assertEqual(getdate(issue.planned_end_date), getdate("2026-11-14"))

	def test_link_backlog_task_later(self):
		"""Setting a sprint on a backlog Task fills only its empty date fields."""
		project = make_project()
		sprint = make_sprint(project.name)
		task = make_work_item("Task", project=project.name, exp_start_date="2026-11-02")

		task.sprint = sprint.name
		task.save()

		self.assertEqual(getdate(task.exp_start_date), getdate("2026-11-02"))
		self.assertEqual(getdate(task.exp_end_date), getdate("2026-11-14"))

	def test_clearing_sprint_keeps_dates(self):
		"""Removing the sprint moves the item to the backlog without touching its dates."""
		project = make_project()
		task = make_work_item("Task", sprint=make_sprint(project.name).name)

		task.sprint = None
		task.save()

		self.assertEqual(task.project, project.name)
		self.assertEqual(getdate(task.exp_end_date), getdate("2026-11-14"))

	def test_sprint_of_other_project_is_rejected(self):
		"""A Task of Project P cannot take a sprint of Project Q."""
		sprint_of_q = make_sprint(make_project().name)

		with self.assertRaises(frappe.ValidationError):
			make_work_item("Task", project=make_project().name, sprint=sprint_of_q.name)

	def test_new_item_in_completed_sprint_is_rejected(self):
		"""Nothing new can be added to a Completed sprint."""
		sprint = make_sprint(make_project().name, status="Completed")

		with self.assertRaises(frappe.ValidationError):
			make_work_item("Issue", sprint=sprint.name)

	def test_existing_item_in_completed_sprint_can_be_edited(self):
		"""Items already in a sprint stay editable after the sprint completes."""
		sprint = make_sprint(make_project().name)
		task = make_work_item("Task", sprint=sprint.name)
		sprint.status = "Completed"
		sprint.save()

		task.description = "Updated after sprint completion"
		task.save()

		self.assertEqual(task.sprint, sprint.name)

	def test_task_cannot_start_working_in_planned_sprint(self):
		"""A Task in a Planned sprint cannot move to Working."""
		task = make_work_item("Task", sprint=make_sprint(make_project().name).name)

		task.status = "Working"
		with self.assertRaises(frappe.ValidationError):
			task.save()

	def test_working_task_cannot_join_completed_or_planned_sprint(self):
		"""A Working Task cannot be moved into a sprint that is not Active."""
		project = make_project()
		task = make_work_item("Task", project=project.name, status="Working")

		task.sprint = make_sprint(project.name).name
		with self.assertRaises(frappe.ValidationError):
			task.save()

	def test_task_can_start_working_in_active_sprint(self):
		"""Working is allowed while the sprint is Active."""
		task = make_work_item("Task", sprint=make_sprint(make_project().name, status="Active").name)

		task.status = "Working"
		task.save()

		self.assertEqual(task.status, "Working")

	def test_working_task_stays_editable_after_sprint_completes(self):
		"""A Task already Working can still be edited once its sprint completes."""
		sprint = make_sprint(make_project().name, status="Active")
		task = make_work_item("Task", sprint=sprint.name, status="Working")
		sprint.status = "Completed"
		sprint.save()

		task.description = "Updated after sprint completion"
		task.save()

		self.assertEqual(task.status, "Working")

	def test_task_dates_outside_sprint_are_rejected(self):
		"""Expected start or end date outside the sprint's range is rejected."""
		sprint = make_sprint(make_project().name)

		with self.assertRaises(frappe.ValidationError):
			make_work_item("Task", sprint=sprint.name, exp_start_date="2026-10-30")
		with self.assertRaises(frappe.ValidationError):
			make_work_item("Task", sprint=sprint.name, exp_end_date="2026-11-20")

	def test_issue_dates_outside_sprint_are_rejected(self):
		"""Planned start or end date outside the sprint's range is rejected."""
		sprint = make_sprint(make_project().name)

		with self.assertRaises(frappe.ValidationError):
			make_work_item("Issue", sprint=sprint.name, planned_start_date="2026-10-30")
		with self.assertRaises(frappe.ValidationError):
			make_work_item("Issue", sprint=sprint.name, planned_end_date="2026-11-20")

	def test_dates_on_sprint_boundaries_are_allowed(self):
		"""The sprint's own start and end dates are inside the range."""
		sprint = make_sprint(make_project().name)

		issue = make_work_item(
			"Issue", sprint=sprint.name, planned_start_date="2026-11-01", planned_end_date="2026-11-14"
		)

		self.assertEqual(getdate(issue.planned_end_date), getdate("2026-11-14"))

	def test_moving_dates_out_of_sprint_on_edit_is_rejected(self):
		"""Changing a date on an existing item is checked against the sprint too."""
		task = make_work_item("Task", sprint=make_sprint(make_project().name).name)

		task.exp_end_date = "2026-11-30"
		with self.assertRaises(frappe.ValidationError):
			task.save()

	def test_new_item_in_sprint_of_closed_project_is_rejected(self):
		"""Tasks and Issues cannot be linked to a sprint whose project is not Open."""
		project = make_project()
		sprint = make_sprint(project.name)
		close_project(project.name, "Completed")

		for doctype in ("Task", "Issue"):
			with self.assertRaises(frappe.ValidationError):
				make_work_item(doctype, sprint=sprint.name)

	def test_backlog_task_cannot_join_sprint_of_cancelled_project(self):
		"""Setting a sprint on an existing Task is checked against the project's status too."""
		project = make_project()
		sprint = make_sprint(project.name)
		task = make_work_item("Task", project=project.name)
		close_project(project.name, "Cancelled")

		task.sprint = sprint.name
		with self.assertRaises(frappe.ValidationError):
			task.save()

	def test_existing_item_stays_editable_after_project_closes(self):
		"""Items already in a sprint can still be edited once their project is Completed."""
		project = make_project()
		task = make_work_item("Task", sprint=make_sprint(project.name).name)
		close_project(project.name, "Completed")

		task.description = "Updated after project completion"
		task.save()

		self.assertEqual(task.project, project.name)
