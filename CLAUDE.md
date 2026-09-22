# RaigonOS

Django gallery-management app: an artist catalogues **Collections** of
**Artworks** behind auth-gated CRUD; the public sees only published
Collections, read-only. Built for Code Institute's Milestone Project 3
(Back End Development unit — see `documentation/` for the assessment PDFs
this project is graded against).

Full project narrative (rationale, UX planes, colour/type, user stories,
security write-up, deployment steps) lives in `README.md` — read that for
context, not just this file. Bug log and testing procedure: `TESTING.md`.

## Stack

Django 5.2 + SQLite locally / PostgreSQL in production (`dj_database_url`,
env-driven). Deployed on Render; static via WhiteNoise; media via
Cloudinary in production (falls back to local disk when Cloudinary env
vars are unset). Single app: `gallery`.

## Layout

- `gallery/` — the only app. `models.py` (Collection, Artwork),
  `views.py` (function-based views only), `forms.py` (plain ModelForms),
  `urls.py` (namespaced `gallery:`), `admin.py`, `tests.py`.
- `raigonos/` — project settings/urls/wsgi.
- `templates/` — global templates (`base.html`, 404, `registration/`).
  `gallery/templates/gallery/` — app templates.
- `static/css/style.css` — hand-written custom CSS (no framework).

## Data model

`Collection` (owner=User FK, title, slug auto-generated+unique, description,
cover_image, status draft/published) `1—N` `Artwork` (title, image
required, medium, year, description, display_order). Both cascade-delete.
Public queries always filter `status=STATUS_PUBLISHED`; owner queries
filter by `owner=request.user` (or `collection__owner`) and 404 (not 403)
on mismatch — see `DashboardPermissionTests` in `gallery/tests.py`.

## Conventions in this codebase

- Function-based views, one `@login_required` per mutating view; ownership
  always re-checked via `get_object_or_404(..., owner=request.user)`, never
  trusted from the URL alone.
- `messages.success(...)` on every create/update/delete, then redirect to
  `gallery:dashboard`.
- Delete views: GET renders a `*_confirm_delete.html` template, POST
  performs the deletion — no JS confirm dialogs.
- Settings are entirely env-var driven (`SECRET_KEY`, `DEBUG`,
  `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, Cloudinary
  creds). `.env` is gitignored; `.env.example` documents the keys.

## Commands

- Run locally: `./run.sh` (or `source venv/bin/activate && python manage.py runserver`)
- Tests: `python manage.py test`
- Migrations: `python manage.py makemigrations && python manage.py migrate`

## Working on this repo

- **Never `git commit` or `git push` without explicit go-ahead** — ask first
  every time, even after a prior approval.
- This is a graded CI submission: check `documentation/` (the assessment
  guide + project requirements PDFs) before adding features, so new work
  stays aligned with what's actually being assessed (CRUD, data modelling,
  security practices, README/testing documentation, clean/PEP8 code).
- README and TESTING.md are living documents the user edits progressively
  (marked with 🚧 for unfinished sections) — keep entries consistent with
  their existing tone and structure if asked to extend them.
