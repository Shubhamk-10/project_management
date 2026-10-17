# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

MODULE = "PM Agile"

CUSTOM_FIELDS = {
	"Task": [
		{
			"fieldname": "sprint",
			"fieldtype": "Link",
			"label": "Sprint",
			"options": "Sprint",
			"insert_after": "project",
			"in_standard_filter": 1,
			"search_index": 1,
		},
		{
			"fieldname": "story_points",
			"fieldtype": "Int",
			"label": "Story Points",
			"insert_after": "sprint",
		},
	],
	"Issue": [
		{
			"fieldname": "sprint",
			"fieldtype": "Link",
			"label": "Sprint",
			"options": "Sprint",
			"insert_after": "project",
			"in_standard_filter": 1,
			"search_index": 1,
		},
		{
			"fieldname": "story_points",
			"fieldtype": "Int",
			"label": "Story Points",
			"insert_after": "sprint",
		},
		{
			"fieldname": "planned_start_date",
			"fieldtype": "Date",
			"label": "Planned Start Date",
			"insert_after": "story_points",
		},
		{
			"fieldname": "planned_end_date",
			"fieldtype": "Date",
			"label": "Planned End Date",
			"insert_after": "planned_start_date",
		},
	],
}


def make_custom_fields() -> None:
	"""
	Create or update the sprint fields on Task and Issue. Safe to re-run; called on install and every migrate.

	Returns:
		None
	"""
	create_custom_fields(__with_module(CUSTOM_FIELDS), update=True)


def delete_custom_fields() -> None:
	"""
	Remove the Custom Field records this app added. Database columns stay, as with any Frappe custom field.

	Returns:
		None
	"""
	for doctype, fields in CUSTOM_FIELDS.items():
		fieldnames = [field["fieldname"] for field in fields]
		frappe.db.delete("Custom Field", {"dt": doctype, "fieldname": ("in", fieldnames)})
		frappe.clear_cache(doctype=doctype)


def __with_module(custom_fields: dict) -> dict:
	"""
	Tag every field with this module so the records are traceable to the app.

	Parameters:
		custom_fields (dict, required): {doctype: [field dict, ...]} as in CUSTOM_FIELDS.

	Returns:
		dict: A new mapping with `module` set on each field dict; the input is not modified.
	"""
	return {
		doctype: [{**field, "module": MODULE} for field in fields]
		for doctype, fields in custom_fields.items()
	}
