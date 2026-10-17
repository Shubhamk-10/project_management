<!--
Copyright (c) 2026 8848 Digital LLP. All rights reserved.
Proprietary and confidential. Unauthorized copying, distribution, or use
of this file, via any medium, is strictly prohibited without prior
written permission from 8848 Digital LLP.
-->

# Project Management 8848

## Overview

Adds sprint planning to ERPNext projects. Project teams plan ERPNext Tasks and
Issues into time-boxed Sprints and follow progress from a single Project Dashboard.
It reuses ERPNext's Project, Task and Issue as they are, extending them only through
custom fields and hooks, so standard ERPNext screens, reports and permissions keep working.

## Key DocTypes

| DocType | Owned by this app? | Purpose |
| ------- | ------------------ | ------- |
| Sprint | Yes | A time-boxed iteration of a Project (Planned → Active → Completed) with a goal and date range. |
| Project | No (ERPNext, unchanged) | The project a sprint and its work items belong to. |
| Task | No (ERPNext, customized) | Gains a Sprint link and story points; dates fill from the sprint. |
| Issue | No (ERPNext, customized) | Gains a Sprint link, story points and planned start/end dates. |

### Custom fields added to ERPNext

| DocType | Field | Type | Placed after |
| ------- | ----- | ---- | ------------ |
| Task | Sprint | Link to Sprint | Project |
| Task | Story Points | Integer | Sprint |
| Issue | Sprint | Link to Sprint | Project |
| Issue | Story Points | Integer | Sprint |
| Issue | Planned Start Date | Date | Story Points |
| Issue | Planned End Date | Date | Planned Start Date |

The fields are created on install and re-applied on every migrate, and removed when the app is uninstalled.

## Features

- **Project Management workspace** with live number cards (Active Sprints, Open Tasks,
  Overdue Tasks, Open Issues), Tasks and Issues by status charts, and shortcuts.
- **Project Dashboard** (`/app/pm-projects`, or `/app/pm-projects/<project>` as a direct link):
  pick an open project to see
  - its sprints, newest first, with status, dates, goal and Tasks/Issues done out of total;
  - a Backlog card for items not yet planned into a sprint;
  - Task and Issue counts by status, plus an overdue count.

  Every count opens the matching filtered list. The dashboard remembers each user's last project.
- **Create from anywhere:** New Sprint, Task or Issue from the dashboard. A Task or Issue
  can be put straight into an open sprint or left in the backlog. On a Sprint, use Create > Task / Issue.
- **Automatic linking:** a Task or Issue placed in a sprint takes the sprint's project, and
  its empty date fields take the sprint's start and end dates (expected dates on Task, planned
  dates on Issue). Dates already entered are kept. Removing the sprint returns the item to the backlog.
- **Guard rails:** a project has at most one Active sprint. A sprint must end on or after its start.
  An item cannot be placed in a sprint of a different project or added to a Completed sprint.
  These rules apply to form saves, Quick Entry, Data Import and the REST API alike.

## Integrations

None. The app works entirely within ERPNext.

## Installation

    bench get-app project_management_8848 <repo_url> --branch develop
    bench --site <site_name> install-app project_management_8848
    bench --site <site_name> migrate

Requires ERPNext v15.

## Development

Run the tests on a separate test site, never on a working site:

    bench --site <test_site> set-config allow_tests true
    bench --site <test_site> run-tests --app project_management_8848

The repository uses `pre-commit` (ruff, eslint, prettier); run `pre-commit install` once in
`apps/project_management_8848`.

## App Structure

Module-level layout (DocTypes, customizations, dashboard, workspace) is described in
[project_management_8848/pm_agile/README.md](./project_management_8848/pm_agile/README.md).

## Maintainers

8848 Digital LLP — shubham@8848digital.com

## License

Proprietary — Copyright (c) 2026 8848 Digital LLP. All rights reserved.
See [license.txt](license.txt) for details.
