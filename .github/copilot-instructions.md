# Copilot instructions for Barangay Complaint & Feedback Portal

A Django web application for managing barangay complaints and feedback with role-based access control (Resident, Secretary, Chairman). Built with Django 4.2+, Bootstrap 5, and PostgreSQL/SQLite support.

## Overview
Django app with 4 main modules: `accounts` (custom user model with roles), `complaints` (full CRUD with file attachments and status tracking), `feedback` (star ratings with admin responses), and `dashboard` (role-specific views). Uses Django's built-in admin, email notifications, and media file handling. Standard Django project structure with custom templates using Bootstrap 5 and role-based navigation.

## Key directories and responsibilities
- `accounts/`: Custom User model extending AbstractUser with roles (resident/secretary/chairman), approval workflow, registration/login views
- `complaints/`: Complaint model with categories, status tracking, file attachments, email notifications; CRUD views with role-based permissions
- `feedback/`: Star rating system with categories, admin response capability, anonymous options
- `dashboard/`: Role-specific dashboard views (resident/secretary/chairman) with statistics and quick actions
- `templates/`: Bootstrap 5 templates with base template, role-based navigation, responsive design
- `static/css/`: Custom CSS extending Bootstrap with dashboard stat cards, status badges, file upload styling
- `barangay_portal/`: Django settings with custom user model, media handling, email config

## Build/test/debug workflow
```bash
# Initial setup
pip install -r requirements.txt
cp .env.example .env  # Edit with your settings
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create chairman user, set role in admin

# Development
python manage.py runserver  # http://127.0.0.1:8000/
python manage.py shell  # For creating complaint categories
python manage.py collectstatic  # Production static files

# Database operations
python manage.py makemigrations [app_name]
python manage.py migrate
python manage.py dbshell  # Access database directly
```

## Conventions and patterns
- **Role-based access**: Custom User model with `is_resident()`, `is_secretary()`, `can_manage_complaints()` methods; decorators check permissions in views
- **Status tracking**: Complaint model uses choices for status/priority with automatic email notifications via `save()` override
- **File handling**: Uses Django's FileField with custom validation in forms, stored in `media/complaint_attachments/`
- **Templates**: Extends `base.html` with Bootstrap 5, role-specific navigation, status badges with CSS classes like `.status-pending`
- **Forms**: Django ModelForms with Bootstrap widgets via `django-widget-tweaks` and custom CSS classes
- **Admin**: Extensive Django admin customization with inlines, custom displays, filters (see `complaints/admin.py`)

## Integration points
- **Email**: Django's email framework with console backend (dev) and SMTP (production); automatic notifications on complaint status changes
- **File uploads**: Pillow for image handling, file type validation in forms, max 10MB per file
- **Static files**: WhiteNoise for production static file serving
- **Database**: SQLite (dev) with PostgreSQL-ready configuration via DATABASE_URL

## Development gotchas
- New users need chairman approval: set `is_approved=True` in admin after registration
- Custom user model requires migrations from fresh DB: delete `migrations/` folders and remake if changing User model
- File uploads require `MEDIA_ROOT` and `MEDIA_URL` configuration; ensure media directory exists
- Email requires SMTP configuration for production; uses console backend in development
- Bootstrap 5 classes used throughout templates; custom CSS in `static/css/style.css` extends Bootstrap
- Role-based navigation in `base.html` checks user role methods; ensure User model methods are working
- Complaint categories must be created manually via admin or shell after initial migration

This repository currently contains no source files or documentation (checked on 2025-09-19). Use this guide to operate effectively now and to update once code is added.

## Current state and immediate steps
- The workspace root is empty. Do not assume frameworks, languages, or build tools.
- If the goal is to analyze an existing project, request the user to open that repo in this workspace or point to the correct path.
- If the goal is to scaffold a new project, propose a minimal plan with 2–3 options (language, framework, tests) and get explicit confirmation before creating files.

## When code is added: fast-orientation checklist
Use this exact pass to form a mental model and update this file with specifics:
1. Inventory key manifests/configs at the root: one of package.json, pyproject.toml, requirements.txt, Pipfile, poetry.lock, pom.xml, build.gradle, go.mod, Cargo.toml, ".sln/.csproj", Dockerfile, docker-compose.yml, Makefile, Taskfile, README.md.
2. Discover build and test commands from manifests and configs (e.g., npm scripts, Make targets, Gradle/Maven tasks, dotnet CLI, tox/pytest, invoke, just). Prefer project scripts over global tools.
3. Map the architecture:
   - Identify top-level app directories (e.g., src/, app/, services/, packages/, server/, client/) and their responsibilities.
   - Note cross-component communication (HTTP/REST, gRPC, message bus, direct imports) and shared modules.
   - Record data flow boundaries (DB, cache, queues, external APIs) and where clients/adapters live.
4. Capture project-specific conventions: naming, module layout, dependency injection style, error handling, logging patterns, configuration loading, testing style/fixtures.
5. Record environment expectations: required env vars, secrets strategy (.env, user-secrets, KeyVault), and how local dev runs without production credentials.

## How to document here (update once code exists)
Keep this file concise (~20–50 lines) and specific to THIS repo. Replace this section with concrete details and file references:
- Overview: one-paragraph big-picture architecture and why it’s structured that way.
- Key directories and ownership: e.g., `src/api` (HTTP entrypoints), `src/domain` (core logic), `src/integrations` (external services), `tests` (unit + integration layout).
- Build/test/debug workflows: exact commands and any pre-reqs; include non-obvious steps (DB migrations, seed data, local emulators).
- Conventions: coding patterns the repo actually uses (e.g., hexagonal architecture, CQRS, repository pattern, Redux slices, React Query, FastAPI routers, NestJS modules, DI container choices), with 1–2 file examples.
- Integration points: list external services, clients, or SDKs used and where to find their adapters; note how to run locally.
- Gotchas: anything that bites newcomers (path aliases, codegen steps, required pre-commit hooks, monorepo workspaces).

## Agent execution preferences
- Make minimal, targeted edits; preserve existing style and public APIs.
- Prefer reading larger, relevant file chunks over many tiny reads; trace symbol definitions before edits.
- When adding features, include small, runnable tests following the project’s existing test framework and layout.
- Validate changes by running the actual build/tests where configured; surface output succinctly.

## Maintaining this file
- After significant changes (new service, module, or workflow), update the sections above with exact file paths and commands.
- If another `.github/copilot-instructions.md` appears (e.g., after pulling), merge by preserving concrete, repo-specific content and replacing outdated commands.