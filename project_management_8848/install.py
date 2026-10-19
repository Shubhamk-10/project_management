# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from project_management_8848.pm_agile.customization.indexes import add_indexes


def after_sync() -> None:
	"""
	Add the sprint field indexes when the app is installed. Runs as `after_sync`, not
	`after_install`, because Frappe imports fixtures/ (which create the sprint custom fields)
	after `after_install` but before `after_sync`.

	Returns:
		None
	"""
	add_indexes()


def after_migrate() -> None:
	"""
	Re-apply the sprint field indexes so changes reach existing sites.

	Returns:
		None
	"""
	add_indexes()
