# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from project_management_8848.pm_agile.customization.sprint_connections import add_sprint_to_work_item


def get_data(data: dict) -> dict:
	"""
	override_doctype_dashboards hook: show the Issue's sprint in its Connections tab.

	Parameters:
		data (dict, required): ERPNext's Issue dashboard config.

	Returns:
		dict: The config with the Sprint link added.
	"""
	return add_sprint_to_work_item(data)
