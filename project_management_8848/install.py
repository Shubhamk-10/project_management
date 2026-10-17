# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from project_management_8848.pm_agile.customization.custom_fields import (
	delete_custom_fields,
	make_custom_fields,
)
from project_management_8848.pm_agile.customization.indexes import add_indexes


def after_install() -> None:
	"""
	Add the sprint custom fields and their indexes to Task and Issue when the app is installed.

	Returns:
		None
	"""
	make_custom_fields()
	add_indexes()


def after_migrate() -> None:
	"""
	Re-apply the sprint custom fields and indexes so changes reach existing sites.

	Returns:
		None
	"""
	make_custom_fields()
	add_indexes()


def before_uninstall() -> None:
	"""
	Remove the sprint custom fields from Task and Issue before the app is uninstalled.
	Indexes stay with the columns, which Frappe never drops for custom fields.

	Returns:
		None
	"""
	delete_custom_fields()
