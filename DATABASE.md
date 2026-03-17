Database schema and relationships for the project (Django models)

This document describes the database tables, columns, and relationships derived from the Django models you provided: Company, User (extends AbstractUser), Project, Task, and ActivityLog.

## Overview

Models:
- Company
- User (extends Django's AbstractUser)
- Project
- Task
- ActivityLog

All models use standard integer primary keys (Django's default `id` column) unless you've configured a custom PK.

## Entity definitions (Django field)

1) Company
- id: integer PRIMARY KEY (auto)
- name: varchar(255) NOT NULL
- created_at: timestamp with time zone / datetime NOT NULL (auto_now_add)

2) User (extends AbstractUser)
- id: integer PRIMARY KEY (auto)
- username: varchar(150) UNIQUE (from AbstractUser)
- email: varchar(254)
- password: varchar(...) (hashed)
- first_name, last_name: varchar(150)
- is_staff, is_active, is_superuser, last_login, date_joined (from AbstractUser)
- role: varchar(25) NULL (choices from RoleTypeConst)
- company_id: integer NULL -> FK to `company(id)` (on delete CASCADE)

Note: AbstractUser adds many columns (username, email, password, is_active, etc.). Our extra columns are `role` and `company_id`.

3) Project
- id: integer PRIMARY KEY (auto)
- name: varchar(255) NOT NULL
- company_id: integer NOT NULL -> FK to `company(id)` (on delete CASCADE)
- created_by_id: integer NULL -> FK to `accounts_user(id)` (on delete SET NULL)
- created_at: timestamp NOT NULL (auto_now_add)

4) Task
- id: integer PRIMARY KEY (auto)
- status: varchar(25) NULL (choices from StatusTypeConst) DEFAULT 'TODO' (or constant value)
- title: varchar(255) NOT NULL
- description: text NOT NULL
- project_id: integer NOT NULL -> FK to `project(id)` (on delete CASCADE)
- assigned_to_id: integer NULL -> FK to `accounts_user(id)` (on delete SET NULL)
- due_date: date NULL
- created_at: timestamp NOT NULL (auto_now_add)

5) ActivityLog
- id: integer PRIMARY KEY (auto)
- user_id: integer NOT NULL -> FK to `accounts_user(id)` (on delete CASCADE)
- task_id: integer NULL -> FK to `task(id)` (on delete SET NULL)
- action: varchar(255) NOT NULL
- created_at: timestamp NOT NULL (auto_now_add)

## Relationships

- `User.company` -> on_delete=models.CASCADE: deleting a company will delete its users (be careful in production).
- `Project.company` -> on_delete=models.CASCADE: deleting a company removes projects.
- `Project.created_by` -> SET_NULL: preserve project when creator user is deleted.
- `Task.project` -> CASCADE: delete tasks when project deleted.
- `Task.assigned_to` -> SET_NULL: preserve task when assigned user is deleted.
- `ActivityLog.user` -> CASCADE: deleting a user deletes their logs. If you want logs preserved, consider SET_NULL instead.
- `ActivityLog.task` -> SET_NULL: current design keeps logs even if the task is deleted.


### Cardinality & access patterns (table)
| Relationship | FK column | Common access pattern |
|---|---|---|
| Company -> User | accounts_user.company_id | List users by company, enforce company-level multi-tenancy |
| Company -> Project | projects_project.company_id | List projects for a company, filter tasks via project.company_id |
| Project -> Task | tasks_task.project_id | Pull tasks by project, or company via join to project |
| User -> Task (assigned_to) | tasks_task.assigned_to_id | Query tasks assigned to user, unassigned tasks |
| User -> Project (created_by) | projects_project.created_by_id | Track creator, can be null if user removed |
| Task -> ActivityLog | tasks_activitylog.task_id | Append-only log entries for task lifecycle |
| User -> ActivityLog | tasks_activitylog.user_id | Actor of the action; used to audit who performed changes |

### Example JSON payloads
- Create Task

```json
{
  "title": "Finish report",
  "description": "Prepare final report for Q1",
  "project": 12,
  "assigned_to": 5,
  "due_date": "2026-04-01"
}
```

- Update Task (partial)

```json
{
  "status": "IN_PROGRESS",
  "assigned_to": 7
}
``` 