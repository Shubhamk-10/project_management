# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe.tests.utils import FrappeTestCase

from project_management_8848.tests.utils import make_project, make_sprint


class TestSprint(FrappeTestCase):
	"""Sprint controller rules: naming, date range and one Active sprint per project."""

	def test_name_follows_project(self):
		"""Sprint names use the {project}-SPR-{##} format."""
		project = make_project()
		sprint = make_sprint(project.name)

		self.assertEqual(sprint.name, f"{project.name}-SPR-01")

	def test_end_before_start_is_rejected(self):
		"""An end date before the start date throws."""
		project = make_project()

		with self.assertRaises(frappe.ValidationError):
			make_sprint(project.name, start_date="2026-11-14", end_date="2026-11-01")

	def test_single_day_sprint_is_allowed(self):
		"""Start and end on the same day is valid."""
		project = make_project()
		sprint = make_sprint(project.name, start_date="2026-11-01", end_date="2026-11-01")

		self.assertTrue(sprint.name)

	def test_second_active_sprint_is_rejected(self):
		"""A project cannot have two Active sprints."""
		project = make_project()
		make_sprint(project.name, status="Active")

		with self.assertRaises(frappe.ValidationError):
			make_sprint(project.name, status="Active")

	def test_active_sprints_in_different_projects(self):
		"""The one-Active rule is per project."""
		make_sprint(make_project().name, status="Active")
		other = make_sprint(make_project().name, status="Active")

		self.assertEqual(other.status, "Active")

	def test_activate_after_completing_previous(self):
		"""Completing the Active sprint frees the project for the next one."""
		project = make_project()
		first = make_sprint(project.name, status="Active")
		second = make_sprint(project.name)

		first.status = "Completed"
		first.save()
		second.status = "Active"
		second.save()

		self.assertEqual(second.status, "Active")
