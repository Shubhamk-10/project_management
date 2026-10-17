# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from frappe.model.document import Document

from project_management_8848.pm_agile.doctype.sprint.sprint_utils import (
	validate_date_range,
	validate_single_active_sprint,
)


class Sprint(Document):
	"""A time-boxed iteration of an ERPNext Project that Tasks and Issues are planned into."""

	def validate(self):
		"""
		Reject an inverted date range and a second Active sprint in the same project.

		Returns:
			None
		"""
		validate_date_range(self)
		validate_single_active_sprint(self)
