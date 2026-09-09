# RaigonOS

Developer: Railson Gonçalves ([raigonlab](https://www.github.com/raigonlab))

[![GitHub commit activity](https://img.shields.io/github/commit-activity/t/raigonlab/raigonos)](https://www.github.com/raigonlab/raigonos/commits/main)
[![GitHub last commit](https://img.shields.io/github/last-commit/raigonlab/raigonos)](https://www.github.com/raigonlab/raigonos/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/raigonlab/raigonos)](https://www.github.com/raigonlab/raigonos)
[![badge](https://img.shields.io/badge/status-in_development-yellow)](#)

> 🚧 **This README is being written progressively as the project is built.**
> Sections marked with 🚧 are placeholders and will be completed as the
> corresponding feature, wireframe or screenshot is produced.

---

## Project Introduction and Rationale

RaigonOS is a full-stack gallery management platform built with Django and
PostgreSQL, allowing an artist to catalogue, organise and present their art
**Collections** and individual **Artworks** online, with full create, read,
update and delete control over their own content.

It is a conceptual continuation of [raigon](https://raigonlab.github.io/raigon-mmxi) —
a static, single-page gallery built with HTML, CSS and JavaScript only — but
rebuilt entirely from scratch as a dynamic, database-backed application.
No code from that project is reused; only the domain (an artist's digital
gallery) carries over, as permitted by the assessment brief.

**Target audience**

- **Primary — the site owner (artist):** needs a simple, dependable tool to
  manage their portfolio (add/edit/remove Collections and Artworks) without
  touching code.
- **Secondary — visitors:** collectors, peers and the public browsing the
  published gallery.

**Value provided**

- The artist gets a private, authenticated back office to manage their
  public-facing gallery content directly.
- Visitors get organised, structured access to an artist's body of work,
  grouped into Collections.

**Key technical decisions**

- Django + PostgreSQL, with two core related models — `Collection` and
  `Artwork` (one-to-many) — kept deliberately minimal for the MVP.
- Authentication restricts all create/edit/delete actions to the
  authenticated owner; the public gallery remains read-only for visitors.
- Configuration (`SECRET_KEY`, `DEBUG`, `DATABASE_URL`, allowed hosts) is
  entirely environment-variable driven, so the same codebase runs unchanged
  locally (SQLite) and in production (Render + PostgreSQL).

**Long-term vision (explicitly out of scope for this MVP)**

The data model is designed so that a multi-artist mode could be added later
(each artist owning their own Collections), but public multi-artist sign-up
is **not** part of this submission — see [Features](#features) below for the
full MoSCoW breakdown of what is and isn't included now.

#### [Live site →](https://raigonos.onrender.com)

---

## UX

### The 5 Planes of UX

#### 1. Strategy

**Purpose**

- Give an artist full control over publishing and organising their digital
  gallery, without needing to write code.
- Present that gallery to the public in a clean, distraction-free way that
  puts the artwork first.

**Primary User Needs**

- (Owner) Add, edit and remove Collections and Artworks quickly and safely.
- (Owner) Be confident that only they can modify their content.
- (Visitor) Browse Collections and view individual Artworks with clear
  detail (title, medium, year, description).

**Business Goals**

- Prove full CRUD competency against a real relational schema (Collection ↔
  Artwork), satisfying the Back End Development unit's core requirements.
- Deliver a genuinely usable tool, not just a coursework demo — one the
  developer can keep using for their own gallery after submission.

---

#### 2. Scope

**Features (MVP — must-have)**

- Authentication: signup, login, logout.
- Full CRUD on `Collection` (owner only).
- Full CRUD on `Artwork`, linked to a `Collection` (owner only).
- Public, read-only pages listing Collections and their Artworks.

**Features (documented, not built this cycle — see MoSCoW table)**

- Invitation system for private/invite-only Collections.
- Direct contact/inquiry form.
- Multi-artist public sign-up.
- Search and filtering.

**Content Requirements**

- Collection: title, description, cover image, status.
- Artwork: title, image, medium, year, description.

---

#### 3. Structure

**Information Architecture**

🚧 Sitemap to be confirmed once URLs/views are implemented. Planned pages:

- `/` — public gallery home (list of Collections)
- `/collection/<slug>/` — Collection detail (its Artworks)
- `/artwork/<id>/` — Artwork detail
- `/dashboard/` — owner-only management area (CRUD entry points)
- `/accounts/login/`, `/accounts/logout/`, `/accounts/signup/`

**User Flow**

🚧 To be documented with screenshots once the templates exist.

---

#### 4. Skeleton

🚧 Wireframes (mobile/tablet/desktop) are planned before templates are
built, following the same process as the previous project (low-fidelity
sketches → Figma wireframes). Will be added here once produced.

---

#### 5. Surface

**Visual Design (direction, not yet finalised in code)**

- Black & white, gallery-like atmosphere — the artwork is the colour.
- Rounded corners on images and UI elements (not strict 90°).
- Generous whitespace between elements.
- Wordmark-style logo (styled text, no icon).

Visual language is inspired by [raigon.ch](https://www.raigon.ch) —
**for aesthetic direction only**; no content, copy, or functionality from
that site is used here.

---

## Colour Scheme

🚧 Draft palette, to be validated once templates are styled:

| Token | Value |
| ------- | ------- |
| Background | `#ffffff` |
| Surface | `#f5f5f5` |
| Text | `#111111` |
| Muted text | `#6b6b6b` |
| Border | `#e0e0e0` |

---

## Typography

🚧 Not yet finalised. Direction: one distinctive serif or display face for
the wordmark/headings, paired with a clean sans-serif for body text and UI
labels — sourced from Google Fonts.

---

## Wireframes

🚧 To be added before templates are built (see [Skeleton](#4-skeleton)).

---

## User Stories

| Target | Expectation | Outcome |
| ------ | ----------- | ------- |
| As the site owner | I want to sign up and log in securely | So only I can manage my gallery content |
| As the site owner | I want to create a Collection | So I can organise my Artworks by theme or series |
| As the site owner | I want to edit or delete a Collection | So I can keep my gallery accurate and current |
| As the site owner | I want to add an Artwork to a Collection | So visitors can see it presented in context |
| As the site owner | I want to edit or delete an Artwork | So I can correct mistakes or retire pieces |
| As a visitor | I want to browse public Collections | So I can view an artist's body of work |
| As a visitor | I want to view an Artwork's detail | So I can see its title, medium, year and description |
| As a visitor | I want the site to work on any device | So I have a consistent experience on mobile and desktop |

🚧 Full backlog (including could-have / won't-have items) is tracked as
GitHub Issues using MoSCoW prioritisation — see
[Agile Development Process](#agile-development-process).

---

## Features

### Existing Features

🚧 None shipped yet — this project is in active development. This section
will list completed, working features (with screenshots) as they land.

### Planned Features (MoSCoW)

| Priority | Feature |
| -------- | ------- |
| Must-have | Django project, PostgreSQL and initial deployment |
| Must-have | `Collection` model with full CRUD (owner only) |
| Must-have | `Artwork` model with full CRUD (linked to Collection) |
| Must-have | Authentication: login, logout, signup and ownership restriction |
| Must-have | Public gallery pages: browse Collections and Artworks |
| Should-have | Templates and CSS: black & white visual identity |
| Could-have | Invitation system for private Collections |
| Could-have | Contact/inquiry form for direct messages to the artist |
| Won't-have (this cycle) | Multi-artist public sign-up (marketplace mode) |
| Won't-have (this cycle) | Search and filtering across Collections and Artworks |

---

## Tools & Technologies

- Python
- Django
- PostgreSQL (production) / SQLite (local development)
- HTML5
- CSS3 (custom)
- JavaScript
- Gunicorn, WhiteNoise (production serving)
- Pillow (image handling)
- Git & GitHub
- Render (deployment)
- Figma (wireframes) 🚧
- Google Fonts 🚧

---

## Agile Development Process

GitHub Issues are used to plan and track development, prioritised with
MoSCoW labels (must/should/could/won't-have).

🚧 [Link to Issues](https://github.com/raigonlab/raigonos/issues) — to be
populated as issues are created.

---

## Testing

Full manual and automated testing procedure, plus a log of bugs found
and fixed during development, is documented in
[TESTING.md](TESTING.md).

---

## Deployment

### Live Website

Deployed on [Render](https://render.com), with a managed PostgreSQL
instance in the same region.

Deployment steps:

1. Create a **PostgreSQL** instance on Render and copy its **Internal
   Database URL**.
2. Create a **Web Service** on Render, connected to this GitHub repository
   (`main` branch).
3. Set the **Build Command**:
   ```
   pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
   ```
4. Set the **Start Command**:
   ```
   gunicorn raigonos.wsgi:application
   ```
5. In the Web Service's **Environment** settings, set:
   - `SECRET_KEY` — generated via Render's own secure value generator
   - `DEBUG=False`
   - `ALLOWED_HOSTS` — the Render service hostname (e.g. `raigonos.onrender.com`)
   - `CSRF_TRUSTED_ORIGINS` — `https://raigonos.onrender.com`
   - `DATABASE_URL` — the Internal Database URL from step 1
6. Deploy. Render builds the app, runs migrations, and starts Gunicorn
   automatically on every push to `main`.

**Live link:** [https://raigonos.onrender.com](https://raigonos.onrender.com)

### Local Development

To run the project locally:

1. Clone the repository:
   ```
   git clone https://github.com/raigonlab/raigonos.git
   ```
2. Navigate into the project folder:
   ```
   cd raigonos
   ```
3. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Copy `.env.example` to `.env` and fill in local values (a local
   `SECRET_KEY`, `DEBUG=True`, etc.).
6. Apply migrations:
   ```
   python manage.py migrate
   ```
7. Run the development server:
   ```
   python manage.py runserver
   ```
8. Open `http://127.0.0.1:8000` in your browser.

---

## Credits

### Content

- Code Institute materials
- [Django documentation](https://docs.djangoproject.com/)
- Claude (https://claude.com/) — coding assistant used for planning,
  debugging and project support throughout development
- [fonts.google.com](https://fonts.google.com) 🚧

### Media

- All artwork and Collection content, once added, belongs to
  Railson Gonçalves (© Raigon Lab).

---

## Acknowledgements

Special thanks to my mentor, Tim Nelson, for guidance and support
throughout the project.
