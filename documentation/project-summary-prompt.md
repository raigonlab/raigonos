# RaigonOS — Project Summary Prompt

> Paste this into another AI tool (design, coding, or planning) to give it
> full context on this project so it can replicate, extend, or design
> around it.

---

Build **RaigonOS**, a full-stack gallery management platform that lets a
visual artist catalogue, organise and present their art online.

## Domain & Purpose

- **Primary user (site owner/artist):** logs in to a private dashboard to
  create, edit and delete their own **Collections** (themed groups of
  work) and the **Artworks** inside each Collection — no code required.
- **Secondary user (visitor):** browses a public, read-only gallery of
  only the artist's *published* Collections and their Artworks.
- Conceptually: a lightweight, single-artist CMS purpose-built for
  presenting a portfolio — not a general blogging platform, not a
  marketplace (yet).
- Tagline: **"Create · Collect · Legacy"** — create an Artwork, collect
  it into a Collection, build a lasting portfolio.

## Tech Stack

- **Backend:** Python, Django 5.2, PostgreSQL (production) / SQLite
  (local dev)
- **Media storage:** Cloudinary (production) — required because the
  hosting platform's filesystem is ephemeral/wiped on every deploy
- **Static files:** WhiteNoise
- **Deployment:** Render (Gunicorn), Git/GitHub for version control
- **Frontend:** server-rendered Django templates, custom CSS (no
  frontend framework), vanilla JS only where unavoidable
- **Fonts:** Playfair Display (serif, headings — with italic used for
  emphasis inside a heading) + Inter (sans-serif, body/UI), both from
  Google Fonts

## Data Model

Two related models, intentionally minimal:

```
User (Django's built-in auth model)
  └── Collection (FK: owner → User, CASCADE)
        - title, slug (auto-generated, unique)
        - description (optional)
        - cover_image (optional, image upload)
        - status: draft | published
        - created_at, updated_at
        └── Artwork (FK: collection → Collection, CASCADE)
              - title
              - image (required, image upload)
              - medium (optional, e.g. "Digital painting")
              - year (optional)
              - description (optional)
              - display_order (controls manual ordering)
              - created_at, updated_at
```

Rules: only `published` Collections (and their Artworks) are visible to
anonymous visitors; `draft` ones 404 on direct URL access and are
excluded from public listings. Deleting a Collection cascades to delete
its Artworks.

## Core Features (must-have, all implemented)

1. Signup / login / logout (Django's built-in auth + a custom signup
   view using `UserCreationForm`)
2. Full CRUD on Collection, restricted to the authenticated owner
3. Full CRUD on Artwork (nested under a Collection), same restriction
4. Ownership enforcement: a logged-in user attempting to edit/delete
   *another* user's Collection or Artwork gets a 404 (not a 403) —
   deliberately not confirming the resource even exists to non-owners
5. Public pages: Collection list (published only), Collection detail
   (its Artworks), Artwork detail
6. Owner-only Dashboard: lists the owner's own Collections (draft +
   published) with inline Edit/Delete actions and thumbnails for both
   the Collection cover and each Artwork

### Explicitly out of scope for this version (documented, not built)

- Invitation system for private/invite-only Collections
- A direct contact/inquiry form to the artist
- Multi-artist public sign-up (marketplace mode) — though the data
  model (Collection → owner FK) is already shaped to support this later
- Search/filtering across Collections and Artworks

## Pages / URL Structure

```
/                                          — public: list published Collections
/collection/<slug>/                        — public: one Collection + its Artworks
/artwork/<id>/                             — public: one Artwork's detail
/accounts/login/, /logout/, /signup/       — auth
/dashboard/                                — owner-only: manage own Collections
/dashboard/collections/new/                — create Collection
/dashboard/collections/<slug>/edit/        — edit Collection
/dashboard/collections/<slug>/delete/      — delete Collection (confirm page)
/dashboard/collections/<slug>/artworks/new/ — create Artwork in a Collection
/dashboard/artworks/<id>/edit/             — edit Artwork
/dashboard/artworks/<id>/delete/           — delete Artwork (confirm page)
```

## Visual Design System

- **Palette** — warm, neutral, not stark black/white:
  - Background: `#f7f4ee` (cream)
  - Surface (cards, inputs): `#ffffff`
  - Text: `#121212`
  - Muted text / labels: `#8a8578`
  - Border: `#e6e1d6`
- **Shape** — large, consistent border-radius (~20px) on cards, images
  and form inputs; buttons are fully pill-shaped (`border-radius: 999px`)
- **Spacing** — generous whitespace between sections; nothing feels
  cramped
- **Typography** — Playfair Display for all headings (large, ~2.25rem
  for page titles, with `<em>`/italic used inline for emphasis within a
  heading, e.g. "Let's create *something lasting*" style); Inter for
  everything else
- **Wayfinding labels** — small, uppercase, letter-spaced (~0.14em)
  "eyebrow" labels above page titles and status badges (e.g. "Gallery",
  "Collection", "Dashboard", "Published")
- **Logo** — a circular seal/stamp mark: an "R" monogram inside a ring
  of small circular text reading "RAIGON · INK · MMXXIII"; used as an
  image (SVG), not a text wordmark, in the site header
- **Reference inspiration (aesthetic only, not content):** a minimalist,
  editorial, gallery-like portfolio aesthetic — think fine art gallery
  catalogue rather than a typical SaaS dashboard. Real, specific
  content (not Lorem Ipsum); no aggressive autoplay or popups; broken/
  missing URLs redirect gracefully; forms give clear inline validation
  feedback.

## Security & Robustness (already implemented — preserve if replicating)

- All secrets (`SECRET_KEY`, database URL, Cloudinary credentials) come
  from environment variables — never hardcoded, never committed
- `DEBUG=False` in production
- CSRF protection active on every form (including logout, which is a
  POST, not a link)
- Passwords hashed via Django's default PBKDF2 — never stored in
  plaintext
- 15 automated tests cover model behaviour, public visibility rules,
  cross-user permission boundaries, and CRUD operations

## Current Status

Fully functional and deployed: models, CRUD, auth, ownership
permissions, image uploads (via Cloudinary), automated tests, and the
visual identity described above are all implemented and live. Remaining
work is documentation polish (wireframes, manual test log,
responsiveness screenshots) and replacing placeholder/test content with
the artist's real Collections and Artworks — not core functionality.
