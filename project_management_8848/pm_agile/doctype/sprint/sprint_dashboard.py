# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

from frappe import _


def get_data() -> dict:
	"""
	List Tasks and Issues linked through their `sprint` field under the Sprint form's Connections tab.

	Returns:
		dict: Frappe dashboard config with `fieldname` and `transactions`.
	"""
	return {
		"fieldname": "sprint",
		"transactions": [{"label": _("Work Items"), "items": ["Task", "Issue"]}],
	}
