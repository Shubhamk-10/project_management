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
| Task | ERPNext | `sprint`, `story_points` fields; `before_validate` fills project/expected dates from the sprint, `validate` enforces same project and no new items in Completed sprints (`customization/task/task.py`). |
| Issue | ERPNext | `sprint`, `story_points`, `planned_start_date`, `planned_end_date` fields; same hooks as Task (`customization/issue/issue.py`). |

- `customization/custom_fields.py`: the custom field definitions, created on install and migrate.
- `customization/indexes.py`: composite `Issue(project, sprint)` index for the dashboard queries, added on install and migrate.
- `customization/sprint_rules.py`: `SPRINT_FIELD_MAP` and the shared `SprintLink` rules used by both hooks.
  The client copy of the map is `pm.SPRINT_FIELD_MAP` in `public/js/pm_quick_create.js`.

## Pages

- `page/pm_projects`: Project Dashboard (`/app/pm-projects[/<project>]`). Data is built in `pm_projects.py`
  and served by `api/v1/project_dashboard.py`. HTML builders are in `public/js/pm_projects_view.js`.

## Workspaces

- `workspace/project_management`: Project Management. Number cards, status charts, shortcuts
  to the dashboard and lists, and a Masters links card.

## Dashboards

- `number_card/`: Active Sprints, Open Tasks, Overdue Tasks, Open Issues.
- `dashboard_chart/`: Tasks by Status and Issues by Status (Group By, Donut).
