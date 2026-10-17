# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe

# ERPNext indexes Task.project but not Issue.project. The Project Dashboard filters Issues
# by project and groups by sprint, so it gets a composite index.
INDEXES = [
	("Issue", ["project", "sprint"]),
]


def add_indexes() -> None:
	"""
	Add the indexes the dashboard queries rely on. frappe.db.add_index skips existing ones,
	so this is safe on every migrate. Must run after the sprint custom fields exist.

	Returns:
		None
	"""
	for doctype, columns in INDEXES:
		frappe.db.add_index(doctype, columns)
