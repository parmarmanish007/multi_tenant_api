# Multi-Tenant SaaS (multi_tenant_api)

This repository contains a multi-tenant SaaS example with a Django REST API backend and a React frontend.

Repository layout

- `sass_system/` — Django backend app (project root: `sass_system/sass_system`).
  - Apps: `accounts`, `projects`, `tasks`, `common`.
  - API docs served with `drf_yasg` (Swagger/OpenAPI).
- `multi_tenant_ui/sass-system/` — React frontend (Create React App / Vite style structure).

Quick overview

- Backend: Django 4.x, Django REST Framework, Simple JWT for auth, drf_yasg for API docs.
- Frontend: React app in `multi_tenant_ui/sass-system/`.
- Purpose: multi-tenant SaaS setup where Users belong to Companies; Projects belong to Companies; Tasks belong to Projects. `ActivityLog` entries track changes to tasks.

Getting started — prerequisites

- Python 3.9+ (matching your local environment)
- PostgreSQL (or set DB env vars to an alternative engine)
- Node.js + npm or yarn for the frontend
- Git (recommended)

Recommended Python workflow (Windows / cmd.exe)

1. Create and activate a virtual environment (cmd):

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install Python dependencies (if `requirements.txt` exists):

```cmd
pip install -r requirements.txt
```

If `requirements.txt` is missing, install at least:

```cmd
pip install django djangorestframework psycopg2-binary drf-yasg djangorestframework-simplejwt python-dotenv
```

Loading environment variables

This project reads a project-level `.env` file located at the repository root. A template `.env` has been provided. Do NOT commit real secrets to the repo. Add `.env` to `.gitignore` (already included).

Important `.env` variables (already present in the `.env` template):

- SECRET_KEY — Django secret key (keep secret in production)
- DEBUG — True/False
- ALLOWED_HOSTS — comma-separated host list
- DB_ENGINE — e.g. `django.db.backends.postgresql`
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT — DB connection
- EMAIL_* — optional email/SMTP settings
- SIMPLE_JWT_SECRET — optional secret for JWT
- REACT_APP_API_URL — frontend -> backend API base URL

Example (.env)

```properties
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=saas_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
SIMPLE_JWT_SECRET=your_jwt_secret
REACT_APP_API_URL=http://localhost:8000/api
```

Database setup & migrations

1. Ensure your Postgres server is running and the DB `DB_NAME` exists (or create it).
2. Run Django migrations (from the backend project directory):

```cmd
cd sass_system
python manage.py migrate
```

3. (Optional) Create a superuser:

```cmd
python manage.py createsuperuser
```

Run the backend (development)

From the `sass_system` directory:

```cmd
python manage.py runserver
```

By default, Swagger UI is usually exposed at `/swagger/` or `/docs/` depending on `urls.py`. If `drf_yasg` is configured, open `http://localhost:8000/swagger/`.

Run the frontend

From the `multi_tenant_ui/sass-system` directory:

```cmd
cd ..\multi_tenant_ui\sass-system
npm install
npm start
```

(Or use `yarn` if preferred.)

Auth and API

- Authentication: JWT (Simple JWT). Use the token endpoints in `accounts` (a custom TokenObtainPairView was included).
- API endpoints are registered in each app's `urls.py` and routed in the project `urls.py`.

Key backend files to know

- `sass_system/accounts/` — user and company models, serializers, auth views (JWT serializer is customized).
- `sass_system/projects/` — Project model and API.
- `sass_system/tasks/` — Task model and `ActivityLog` model. Views include activity logging for task create/update/delete.
- `sass_system/common/` — shared code, permission helpers, constants (e.g., status choices).

Testing

If your repo contains Django tests, run them from the `sass_system` directory:

```cmd
python manage.py test
```

Linting and formatting

Add and run tools you prefer (flake8, black, isort). Example:

```cmd
pip install black flake8 isort
black .
flake8
```

Deployment notes

- Never commit `.env` with real secrets. Use environment-specific secret stores for production.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS` in production.
- Use a production-ready WSGI server (e.g., Gunicorn + Nginx) and a robust database setup.

Helpful maintenance tasks

- Add `requirements.txt` with pinned dependencies to make setup reproducible:

```cmd
pip freeze > requirements.txt
```

- Create `.env.example` with placeholders and keep `.env` out of source control.

Contributing

If you want to add features or fix bugs:

1. Fork / branch from `main`.
2. Create a descriptive branch and a small focused PR.
3. Run tests and ensure no regressions.

License

Add a license file if you plan to open-source the project.

Need help? Next steps I can do for you

- Create `requirements.txt` and `README` updates with exact pinned packages.
- Replace the secret in `.env` with a placeholder and add `.env.example`.
- Wire `python-dotenv` explicitly in dependencies and add a small `manage.py` startup note.

If you want any of those, tell me which one and I will implement it.
