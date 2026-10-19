<!--
Copyright (c) 2026 8848 Digital LLP. All rights reserved.
Proprietary and confidential. Unauthorized copying, distribution, or use
of this file, via any medium, is strictly prohibited without prior
written permission from 8848 Digital LLP.
-->

# PM Agile

## Purpose

Owns sprint planning on top of ERPNext Projects: the Sprint DocType, the sprint rules on
Task and Issue, the Project Dashboard page and the Project Management workspace.

## DocTypes

| DocType | Purpose |
| ------- | ------- |
| [Sprint](./doctype/sprint/sprint.json) | Time-boxed iteration of a Project; controller rules in `sprint_utils.py`, Connections in `sprint_dashboard.py`, Create > Task / Issue in `sprint.js`. |

## Customizations

| DocType | Owned by | What's customized |
| ------- | -------- | ------------------ |
| Task | ERPNext | `sprint` field; `before_validate` fills project/expected dates from the sprint, `validate` enforces same project, no new items in Completed sprints or in sprints of a project that is not Open, Working only in an Active sprint, and expected dates within the sprint (`customization/task/task.py`); its sprint shows under Connections (`customization/task/task_dashboard.py`). |
| Issue | ERPNext | `sprint`, `planned_start_date`, `planned_end_date` fields; same hooks as Task (planned dates must fall within the sprint; the Working rule is Task-only) (`customization/issue/issue.py`); its sprint shows under Connections (`customization/issue/issue_dashboard.py`). |
| Project | ERPNext | Its sprints are listed under Connections (`customization/project/project_dashboard.py`). |

- Custom fields live in the app's `fixtures/` (`task.json`, `issue.json`), exported from records tagged
  module `PM Agile` by `bench --site <site> 8848-export-fixtures --app project_management_8848`.
  Frappe imports them on install and on every `bench migrate`. Edit them in Desk, then re-export. Frappe removes them on uninstall via their module link.
- `customization/indexes.py`: composite `Issue(project, sprint)` index for the dashboard queries, added after install (`after_sync`, once fixtures exist) and on every migrate.
- `customization/sprint_rules.py`: `SPRINT_FIELD_MAP` and the shared `SprintLink` rules used by both hooks.
  The client copy of the map is `pm.SPRINT_FIELD_MAP` in `public/js/pm_quick_create.js`.
- `customization/sprint_connections.py`: the Sprint entries added to the Project, Task and Issue Connections tabs.

## Pages

- `page/pm_projects`: Project Dashboard (`/app/pm-projects[/<project>]`). Data is built in `project_dashboard.py`
  (module root) and served by `api/v1/project_dashboard.py`. HTML builders are in `public/js/pm_projects_view.js`.

## Workspaces

- `workspace/project_management`: Project Management. Number cards, status charts, shortcuts
  to the dashboard and lists, and a Masters links card.

## Dashboards

- `number_card/`: Active Sprints, Open Tasks, Overdue Tasks, Open Issues.
- `dashboard_chart/`: Tasks by Status and Issues by Status (Group By, Donut).
