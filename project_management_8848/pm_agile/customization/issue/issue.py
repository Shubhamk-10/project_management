# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from frappe.model.document import Document

from project_management_8848.pm_agile.customization.sprint_rules import (
	fill_from_sprint,
	validate_sprint_link,
)


def before_validate(doc: Document, method: str | None = None) -> None:
	"""
	doc_events hook: fill the Issue's empty project and planned dates from its sprint.

	Parameters:
		doc (Document, required): The Issue being saved.
		method (str, optional): Hook event name passed by Frappe.

	Returns:
		None
	"""
	fill_from_sprint(doc)


def validate(doc: Document, method: str | None = None) -> None:
	"""
	doc_events hook: block a sprint from another project or a newly linked Completed sprint.

	Parameters:
		doc (Document, required): The Issue being saved.
		method (str, optional): Hook event name passed by Frappe.

	Returns:
		None
	"""
	validate_sprint_link(doc)
