# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from project_management_8848.pm_agile.customization.sprint_connections import add_sprints_to_project


def get_data(data: dict) -> dict:
	"""
	override_doctype_dashboards hook: add the Project's sprints to its Connections tab.

	Parameters:
		data (dict, required): ERPNext's Project dashboard config.

	Returns:
		dict: The config with Sprint added.
	"""
	return add_sprints_to_project(data)
