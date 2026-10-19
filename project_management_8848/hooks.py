# Copyright (c) 2026 8848 Digital LLP. All rights reserved.
# Proprietary and confidential. Unauthorized copying, distribution, or use
# of this file, via any medium, is strictly prohibited without prior
# written permission from 8848 Digital LLP.

app_name = "project_management_8848"
app_title = "Project Management 8848"
app_publisher = "8848 Digital LLP"
app_description = "Sprint-based project management on ERPNext Projects, Tasks and Issues"
app_email = "shubham@8848digital.com"
app_license = "Proprietary"

required_apps = ["erpnext"]

app_include_js = "/assets/project_management_8848/js/pm_quick_create.js"

doctype_js = {
	"Task": "public/js/sprint_filter.js",
	"Issue": "public/js/sprint_filter.js",
}

after_sync = "project_management_8848.install.after_sync"
after_migrate = "project_management_8848.install.after_migrate"

override_doctype_dashboards = {
	"Project": "project_management_8848.pm_agile.customization.project.project_dashboard.get_data",
	"Task": "project_management_8848.pm_agile.customization.task.task_dashboard.get_data",
	"Issue": "project_management_8848.pm_agile.customization.issue.issue_dashboard.get_data",
}

doc_events = {
	"Task": {
		"before_validate": "project_management_8848.pm_agile.customization.task.task.before_validate",
		"validate": "project_management_8848.pm_agile.customization.task.task.validate",
	},
	"Issue": {
		"before_validate": "project_management_8848.pm_agile.customization.issue.issue.before_validate",
		"validate": "project_management_8848.pm_agile.customization.issue.issue.validate",
	},
}

custom_fixtures = [{"dt": "Custom Field", "filters": {"module": "PM Agile"}}]

commands = ["project_management_8848.commands.export_fixtures.export_fixtures"]
