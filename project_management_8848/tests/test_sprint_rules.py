# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate

from project_management_8848.tests.utils import make_project, make_sprint, make_work_item


class TestSprintRules(FrappeTestCase):
	"""Task/Issue doc_events: fill from sprint, same project, no new items in a Completed sprint."""

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
