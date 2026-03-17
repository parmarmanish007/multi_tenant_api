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

## Entity definitions (Django field -> SQL type)

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

## Relationships and cardinality

- Company 1 --- * User
  - One company can have many users. (`User.company` FK)
- Company 1 --- * Project
  - A project belongs to a single company; a company can have many projects. (`Project.company` FK)
- User 1 --- * Project (created_by)
  - A project may be created by a user; `created_by` can be NULL.
- Project 1 --- * Task
  - Each task belongs to a single project; a project can have many tasks. (`Task.project` FK)
- User 1 --- * Task (assigned_to)
  - A task may be assigned to a user; `assigned_to` can be NULL.
- User 1 --- * ActivityLog
  - Each ActivityLog is created by a user (actor) and is required.
- Task 1 --- * ActivityLog (nullable)
  - ActivityLog.task is nullable and uses SET NULL on task deletion; logs persist even if task is deleted.

ER diagram (text):

Company (id, name)
    |1
    |\
    | *
   User (id, username, role, company_id)

Company (id) 1 --- * Project (id, name, company_id, created_by_id)
Project (id) 1 --- * Task (id, title, description, project_id, assigned_to_id)
Task (id) 1 --- * ActivityLog (id, user_id, task_id, action)
User (id) 1 --- * ActivityLog (id, user_id)

## SQL CREATE TABLE (example, PostgreSQL-like)

-- Company
CREATE TABLE company (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- User (only extra columns shown; AbstractUser fields are omitted for brevity)
CREATE TABLE accounts_user (
  id SERIAL PRIMARY KEY,
  username VARCHAR(150) UNIQUE NOT NULL,
  -- ... other AbstractUser fields ...
  role VARCHAR(25),
  company_id INTEGER REFERENCES company(id) ON DELETE CASCADE
);

-- Project
CREATE TABLE projects_project (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  company_id INTEGER NOT NULL REFERENCES company(id) ON DELETE CASCADE,
  created_by_id INTEGER REFERENCES accounts_user(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Task
CREATE TABLE tasks_task (
  id SERIAL PRIMARY KEY,
  status VARCHAR(25),
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  project_id INTEGER NOT NULL REFERENCES projects_project(id) ON DELETE CASCADE,
  assigned_to_id INTEGER REFERENCES accounts_user(id) ON DELETE SET NULL,
  due_date DATE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- ActivityLog
CREATE TABLE tasks_activitylog (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
  task_id INTEGER REFERENCES tasks_task(id) ON DELETE SET NULL,
  action VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

## Indexes and optimizations
- Django will create indexes for foreign keys automatically in many DB backends. Consider adding explicit indexes for frequently queried columns, e.g., `Task.assigned_to`, `Task.project`, and `Project.company`.
- If you query tasks by `status`, add an index on `tasks_task(status)`.

## Constraints / on_delete choices summary
- `User.company` -> on_delete=models.CASCADE: deleting a company will delete its users (be careful in production).
- `Project.company` -> on_delete=models.CASCADE: deleting a company removes projects.
- `Project.created_by` -> SET_NULL: preserve project when creator user is deleted.
- `Task.project` -> CASCADE: delete tasks when project deleted.
- `Task.assigned_to` -> SET_NULL: preserve task when assigned user is deleted.
- `ActivityLog.user` -> CASCADE: deleting a user deletes their logs. If you want logs preserved, consider SET_NULL instead.
- `ActivityLog.task` -> SET_NULL: current design keeps logs even if the task is deleted.

## Django Migrations notes
- Use `python manage.py makemigrations` and `python manage.py migrate` to create these tables.
- If you change `AUTH_USER_MODEL` (custom user), set it early and before first migration to avoid migration complexity.

## Helpful commands (Windows cmd.exe)

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# To create a graphviz ER diagram (optional, requires django-extensions & graphviz):
# 1) Install django-extensions and graphviz
#    pip install django-extensions graphviz
# 2) Add 'django_extensions' to INSTALLED_APPS
# 3) Generate graph
python manage.py graph_models -a -o er_diagram.png

## Example queries

- Get all tasks for a company:
SELECT t.* FROM tasks_task t
JOIN projects_project p ON t.project_id = p.id
WHERE p.company_id = <company_id>;

- Activity log for a task (most-recent first):
SELECT * FROM tasks_activitylog WHERE task_id = <task_id> ORDER BY created_at DESC;

## Quick mapping: Django field -> SQL
- models.CharField(max_length=N) -> VARCHAR(N)
- models.TextField() -> TEXT
- models.DateField() -> DATE
- models.DateTimeField(auto_now_add=True) -> TIMESTAMP WITH TIME ZONE DEFAULT now()
- models.ForeignKey(Model, on_delete=...) -> INTEGER REFERENCES model(id) ...

## Next steps / suggestions
- If you need audit-preserving behavior for users (keep logs even if user deleted), change `ActivityLog.user` to `SET_NULL` and allow NULL.
- Add `updated_at = models.DateTimeField(auto_now=True)` to models you update frequently (Task, Project) to track edits.
- Add constraints or unique_together if you have business rules (e.g., unique project name per company).

---
If you'd like, I can:
- Add `DATABASE.md` into your repo (done), or update your main `README.md` instead.
- Produce a migration-safe SQL dump or generate an ER image using django-extensions (I can add instructions and run it if you want).
- Change `ActivityLog.user` to SET_NULL if you prefer logs always preserved.

Tell me which follow-up you want and I'll proceed.

## Design structure (added)

This section summarizes the design decisions, relationship names, FK constraint names, cardinality table, normalization, and a short lifecycle for Task updates (how ActivityLog entries are created).

### Foreign key constraint names (recommended)
When applying custom SQL or reviewing migrations, you may see FK constraint names generated by Django. Example recommended names to look for in the DB:
- projects_project.company_id -> fk_projects_project_company_id
- projects_project.created_by_id -> fk_projects_project_created_by_id
- tasks_task.project_id -> fk_tasks_task_project_id
- tasks_task.assigned_to_id -> fk_tasks_task_assigned_to_id
- accounts_user.company_id -> fk_accounts_user_company_id
- tasks_activitylog.user_id -> fk_tasks_activitylog_user_id
- tasks_activitylog.task_id -> fk_tasks_activitylog_task_id

Use these names as a reference when writing manual migration SQL or debugging referential integrity errors.

### Cardinality & access patterns (table)
| Relationship | Cardinality | FK column | Common access pattern |
|---|---:|---|---|
| Company -> User | 1 : * | accounts_user.company_id | List users by company, enforce company-level multi-tenancy |
| Company -> Project | 1 : * | projects_project.company_id | List projects for a company, filter tasks via project.company_id |
| Project -> Task | 1 : * | tasks_task.project_id | Pull tasks by project, or company via join to project |
| User -> Task (assigned_to) | 1 : * (nullable) | tasks_task.assigned_to_id | Query tasks assigned to user, unassigned tasks |
| User -> Project (created_by) | 1 : * (nullable) | projects_project.created_by_id | Track creator, can be null if user removed |
| Task -> ActivityLog | 1 : * (nullable) | tasks_activitylog.task_id | Append-only log entries for task lifecycle |
| User -> ActivityLog | 1 : * | tasks_activitylog.user_id | Actor of the action; used to audit who performed changes |

### Normalization & constraints
- The design follows 3NF: attributes belong to the entity that owns them (e.g. task fields live on Task, not duplicated on Project or User).
- Consider adding unique constraints where business rules require them (e.g., unique project name per company: `UniqueConstraint(fields=['company','name'], name='uq_project_company_name')`).
- Consider `NOT NULL` where appropriate. For example, Task.title and Task.description are required in the model; keep them NOT NULL in the DB.

### Recommended indexes
- tasks_task(project_id) — frequent joins and filters by project
- tasks_task(assigned_to_id) — to find tasks for a user quickly
- projects_project(company_id) — to list projects by company
- tasks_task(status) — if you query/filter often by status
- tasks_activitylog(task_id, created_at DESC) — faster retrieval of a task's recent logs

When using PostgreSQL and large datasets, consider BRIN/GIN indexes for large text searches or date ranges.

### Soft deletes, cascade vs preservation
- Currently: Company, Project cascade deletes child records. This is aggressive for multi-tenant apps. If you want stronger preservation, change to SET_NULL and enforce soft-delete flags (e.g., `is_deleted`) at the application level.
- `ActivityLog.task` is SET_NULL so that logs remain when Task is deleted. If you prefer to always keep logs and not delete tasks accidentally, use soft deletes on Task instead of hard delete.

### Task update lifecycle (logging flow)
This describes the flow for updating a Task and creating an `ActivityLog` entry. It maps to the logging code you pasted and the proposed `TaskService` that centralizes logging.

1. View receives an update request for Task X.
2. View obtains `instance = self.get_object()` and captures `old_values` of key fields.
3. Request data is validated via serializer.
4. Service updates the instance (either via serializer.save() or manual field assignment) and returns the updated instance.
5. Compute diffs between `old_values` and new instance values for fields: `status`, `title`, `description`, `project_id`, `assigned_to_id`, `due_date`.
6. Build an `action` string summarizing changes (e.g., "updated task: Title | status: TODO -> IN_PROGRESS; assigned_to_id: 5 -> 7").
7. Create ActivityLog: `ActivityLog.objects.create(user=request.user, task=updated_instance, action=action)`.

Pseudocode (TaskService.execute):

```python
def execute(user, instance, validated_data):
    # capture old values
    old = { ... }
    # perform update
    for k, v in validated_data.items():
        setattr(instance, k, v)
    instance.save()
    # compute diffs and create ActivityLog
    ActivityLog.objects.create(user=user, task=instance, action=action)
    return instance
```

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

### ER diagram (ASCII)

Company(id, name)
  |1
  |\
  | *
 User(id, username, role, company_id)

Company(id) 1 --- * Project(id, name, company_id, created_by_id)
Project(id) 1 --- * Task(id, title, description, project_id, assigned_to_id)
Task(id) 1 --- * ActivityLog(id, user_id, task_id, action)
User(id) 1 --- * ActivityLog(id, user_id)

### ER diagram (Graphviz DOT)

```dot
digraph ER {
  node [shape=record];
  Company [label="{Company|id: PK\lname: varchar(255)\lcreated_at: timestamp\l}"];
  User [label="{User|id: PK\lusername\lrole\lcompany_id: FK -> Company.id\l}"];
  Project [label="{Project|id: PK\lname\lcompany_id: FK -> Company.id\lcreated_by_id: FK -> User.id\l}"];
  Task [label="{Task|id: PK\lstatus\ltitle\ldescription\lproject_id: FK -> Project.id\lassigned_to_id: FK -> User.id\ldue_date\l}"];
  ActivityLog [label="{ActivityLog|id: PK\luser_id: FK -> User.id\ltask_id: FK -> Task.id\laction\l}"];

  Company -> User [label="1..*", arrowhead=none];
  Company -> Project [label="1..*", arrowhead=none];
  Project -> Task [label="1..*", arrowhead=none];
  User -> Task [label="1..*", arrowhead=none, style=dashed];
  Task -> ActivityLog [label="1..*", arrowhead=none];
  User -> ActivityLog [label="1..*", arrowhead=none];
}
```

You can paste the DOT into an online Graphviz renderer or use `graph_models` from `django-extensions` to generate diagrams automatically.

### Small checklist before production deployment
- Verify `AUTH_USER_MODEL` is set and migrations are in place before creating production users.
- Add DB backups and retention policy.
- Revisit cascade deletes: consider soft deletes for Company/Project if accidental data loss is a concern.
- Add monitoring on long running queries (index missing) and add indexes accordingly.

---
If you'd like, I can also:
- Generate a `.png` ER diagram and commit it to the repo (requires installing `django-extensions` and `graphviz`). I can add instructions or run the commands for you.
- Implement `TaskService.execute` in `sass_system/tasks/service.py` and update `sass_system/tasks/views.py` to call it for all create/update/delete actions (and add tests). 
Which one should I do next?