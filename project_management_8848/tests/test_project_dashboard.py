# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe.tests.utils import FrappeTestCase

from project_management_8848.pm_agile.project_dashboard import get_dashboard_data
from project_management_8848.tests.utils import make_project, make_sprint, make_work_item


class TestProjectDashboard(FrappeTestCase):
	"""Counts returned to the Project Dashboard page."""

	def test_sprint_and_backlog_counts(self):
		"""Done/total per sprint, backlog counts and status totals come from the grouped queries."""
		project = make_project()
		sprint = make_sprint(project.name)
		make_work_item("Task", sprint=sprint.name)
		make_work_item("Task", sprint=sprint.name, status="Completed")
		make_work_item("Task", project=project.name)
		make_work_item("Issue", project=project.name)

		data = get_dashboard_data(project.name)

		self.assertEqual(data["sprints"][0]["counts"]["Task"], {"done": 1, "total": 2})
		self.assertEqual(data["sprints"][0]["counts"]["Issue"], {"done": 0, "total": 0})
		self.assertEqual(data["backlog"]["Task"], {"done": 0, "total": 1})
		self.assertEqual(data["backlog"]["Issue"], {"done": 0, "total": 1})
		self.assertEqual(data["work_items"]["Task"]["total"], 3)

	def test_unknown_project_is_rejected(self):
		"""A missing project raises DoesNotExistError, which the API maps to 404."""
		with self.assertRaises(frappe.DoesNotExistError):
			get_dashboard_data("Missing Project For PM Test")
