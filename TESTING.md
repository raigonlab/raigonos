# Testing

> Return back to the [README.md](README.md) file.

---

## Automated Testing

60 automated tests live in `gallery/tests.py`, covering models, public
visibility rules, ownership permissions, and CRUD operations. Run them
with:

```bash
python manage.py test
```

| Test class | Covers |
| ---------- | ------ |
| `CollectionModelTests` | Slug auto-generation from title, uniqueness of duplicate-title slugs, `__str__` |
| `ArtworkModelTests` | `__str__` |
| `PublicGalleryViewTests` | Public pages only list `published` Collections; `draft` Collections 404 on direct access |
| `ArtworkDetailNavigationTests` | Previous/Next links and position counter on the public Artwork detail page |
| `CollectionListViewTests` | Each row on the public Collections list shows the right count, year range and description |
| `ArtworkGalleryViewTests` | Public home page: only published Artworks listed; site menu links vary by auth state |
| `DashboardPermissionTests` | Dashboard requires login; a user cannot edit or delete another user's Collection/Artwork (404, not just hidden) |
| `DashboardSearchTests` | Title search (`?q=`) on the main dashboard list |
| `CollectionManageViewTests` | Per-Collection dashboard page: login required, 404 for non-owner, shows its Artworks |
| `ArtworkManageViewTests` | Artwork preview page: permission checks plus Previous/Next neighbour logic |
| `CollectionCrudTests` | Create/update/delete via the dashboard forms; blank required field is rejected; deleting a Collection cascades to its Artworks |
| `ArtworkCrudTests` | Create/update/delete an Artwork via the dashboard forms; blank required field is rejected |
| `BulkActionTests` | Bulk status changes and bulk delete via "Select" mode; another user's items are silently excluded |
| `EditFormThumbnailTests` | The custom image-preview widget shows on Edit forms, not on Create forms |
| `ArtworkListViewTests` | "All Artworks" page only shows the logged-in owner's own Artworks |
| `CollectionArchiveTests` | Archive status: hidden from public/dashboard, own Archive page, archive/unarchive is POST-only and always lands on Draft |

**Result:** 60/60 passing.

```
Ran 60 tests in 20.753s

OK
```

---

## Code Validation

### Python (PEP8)

Validated with [flake8](https://flake8.pycqa.org/) against all custom
code (`gallery/`, `raigonos/`, `manage.py`, migrations excluded):

```bash
flake8 --max-line-length=99 --exclude=venv,migrations gallery raigonos manage.py
```

**Result:** no errors, no warnings.

### HTML

Validated with the [W3C Nu HTML Checker](https://validator.w3.org/nu/)
against the deployed pages.

| Page | URL checked | Result | Screenshot |
| ---- | ----------- | ------ | ---------- |
| Public gallery home | https://raigonos.onrender.com/ | 0 errors, 0 warnings | |
| Login | https://raigonos.onrender.com/accounts/login/ | 0 errors, 0 warnings | |
| Signup | https://raigonos.onrender.com/accounts/signup/ | 0 errors, 0 warnings | |
| 404 | https://raigonos.onrender.com/pagina-que-nao-existe/ | 0 errors, 0 warnings | <a href="documentation/validation/404-html-terminal.png"><img src="documentation/validation/404-html-terminal.png" width="140" alt="screenshot"></a> — the checker's "Validate by URI" refuses pages with a non-200 status, same as it did for the dashboard pages, so the HTML was fetched directly and POSTed to the checker instead |
| Collections | https://raigonos.onrender.com/collections/ | 0 errors, 0 warnings | <a href="documentation/validation/html/collections.png"><img src="documentation/validation/html/collections.png" width="140" alt="collections.png"></a> |
| Collection detail | https://raigonos.onrender.com/collection/flow-lines/ | 0 errors, 0 warnings | <a href="documentation/validation/html/collection-detail.png"><img src="documentation/validation/html/collection-detail.png" width="140" alt="collection-detail.png"></a> |
| Artwork detail | https://raigonos.onrender.com/artwork/25/ | 0 errors, 0 warnings | <a href="documentation/validation/html/artwork-detail.png"><img src="documentation/validation/html/artwork-detail.png" width="140" alt="artwork-detail.png"></a> |

Dashboard pages require login, so the checker can't fetch them by URL —
each was validated via "Validate by Direct Input" (page source copied
from an authenticated session):

| Page | Result | Screenshot |
| ---- | ------ | ---------- |
| Dashboard — Collections | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-collections.png"><img src="documentation/validation/html/dashboard-collections.png" width="140" alt="dashboard-collections.png"></a> |
| Dashboard — Archive | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-archive.png"><img src="documentation/validation/html/dashboard-archive.png" width="140" alt="dashboard-archive.png"></a> |
| Dashboard — All Artworks | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-all-artworks.png"><img src="documentation/validation/html/dashboard-all-artworks.png" width="140" alt="dashboard-all-artworks.png"></a> |
| Dashboard — Collection page | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-collection-page.png"><img src="documentation/validation/html/dashboard-collection-page.png" width="140" alt="dashboard-collection-page.png"></a> |
| Dashboard — Artwork preview | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-artwork-preview.png"><img src="documentation/validation/html/dashboard-artwork-preview.png" width="140" alt="dashboard-artwork-preview.png"></a> |
| Collection form (create) | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-collection-form.png"><img src="documentation/validation/html/dashboard-collection-form.png" width="140" alt="dashboard-collection-form.png"></a> |
| Artwork form (create) | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-artwork-form.png"><img src="documentation/validation/html/dashboard-artwork-form.png" width="140" alt="dashboard-artwork-form.png"></a> |
| Collection — confirm delete | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-collection-confirm-delete.png"><img src="documentation/validation/html/dashboard-collection-confirm-delete.png" width="140" alt="dashboard-collection-confirm-delete.png"></a> |
| Artwork — confirm delete | 0 errors, 0 warnings | <a href="documentation/validation/html/dashboard-artwork-confirm-delete.png"><img src="documentation/validation/html/dashboard-artwork-confirm-delete.png" width="140" alt="dashboard-artwork-confirm-delete.png"></a> |
| Bulk — confirm delete | 0 errors, 0 warnings | <a href="documentation/validation/dashboard-html-terminal.png"><img src="documentation/validation/dashboard-html-terminal.png" width="140" alt="dashboard-html-terminal.png"></a> — reached via a scripted authenticated request rather than a browser, since it's only rendered mid-flow (Select → Delete) |

All 10 were cross-checked with a second method: HTML fetched through an
authenticated Django test-client session, POSTed straight to the W3C
Nu Checker's HTTP API for each template — same result, 0 errors/0
warnings across the board (screenshot above).

### CSS

Validated with the
[W3C Jigsaw CSS Validator](https://jigsaw.w3.org/css-validator/)
against the deployed stylesheet.

| File | Result |
| ---- | ------ |
| `static/css/style.css` | Valid CSS3. 0 errors, 15 warnings — 7 "CSS variables are not statically checked" (the validator can't resolve `var(--font-serif)`/`var(--font-sans)`, both of which do end in a generic fallback), 8 vendor-prefix notices (`-webkit-user-select`, `-webkit-user-drag`, `-webkit-font-smoothing`, `-webkit-backdrop-filter`, `-webkit-appearance`, `::-webkit-details-marker` ×2) — all intentional, same reasoning as the `-apple-system` fallback |

![CSS validation, 0 errors](documentation/validation/css-validation.png)

### JavaScript

Linted with [JSHint](https://jshint.com) (`v2.13.6`, run via `npx jshint`)
against every custom JS file:

```bash
npx jshint static/js/dashboard.js static/js/exhibition.js static/js/site-menu.js static/js/artwork-detail.js
```

| File | Result |
| ---- | ------ |
| `static/js/dashboard.js` | 0 errors, 0 warnings |
| `static/js/exhibition.js` | 0 errors, 0 warnings |
| `static/js/site-menu.js` | 0 errors, 0 warnings |
| `static/js/artwork-detail.js` | 0 errors, 0 warnings |

![JSHint run, exit code 0](documentation/validation/jshint-terminal.png)

---

## Responsiveness

Public pages tested against the deployed site at three breakpoints —
Mobile 375×812, Tablet 768×1024, Desktop 1440×900 — using a real Chrome
instance with the viewport set directly via CDP (not just a resized
window), so each screenshot reflects genuine layout at that width.
Screenshots saved to `documentation/responsiveness/`.

| Section | Mobile | Tablet | Desktop |
| ------- | ------ | ------ | ------- |
| Public gallery home (exhibition) | <a href="documentation/responsiveness/home-mobile.png"><img src="documentation/responsiveness/home-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/home-tablet.png"><img src="documentation/responsiveness/home-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/home-desktop.png"><img src="documentation/responsiveness/home-desktop.png" width="140" alt="screenshot"></a> |
| Collections | <a href="documentation/responsiveness/collections-mobile.png"><img src="documentation/responsiveness/collections-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/collections-tablet.png"><img src="documentation/responsiveness/collections-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/collections-desktop.png"><img src="documentation/responsiveness/collections-desktop.png" width="140" alt="screenshot"></a> |
| Collection detail | <a href="documentation/responsiveness/collection-detail-mobile.png"><img src="documentation/responsiveness/collection-detail-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/collection-detail-tablet.png"><img src="documentation/responsiveness/collection-detail-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/collection-detail-desktop.png"><img src="documentation/responsiveness/collection-detail-desktop.png" width="140" alt="screenshot"></a> |
| Artwork detail | <a href="documentation/responsiveness/artwork-detail-mobile.png"><img src="documentation/responsiveness/artwork-detail-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/artwork-detail-tablet.png"><img src="documentation/responsiveness/artwork-detail-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/artwork-detail-desktop.png"><img src="documentation/responsiveness/artwork-detail-desktop.png" width="140" alt="screenshot"></a> |
| Login | <a href="documentation/responsiveness/login-mobile.png"><img src="documentation/responsiveness/login-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/login-tablet.png"><img src="documentation/responsiveness/login-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/login-desktop.png"><img src="documentation/responsiveness/login-desktop.png" width="140" alt="screenshot"></a> |
| Signup | <a href="documentation/responsiveness/signup-mobile.png"><img src="documentation/responsiveness/signup-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/signup-tablet.png"><img src="documentation/responsiveness/signup-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/signup-desktop.png"><img src="documentation/responsiveness/signup-desktop.png" width="140" alt="screenshot"></a> |
| 404 | <a href="documentation/responsiveness/404-mobile.png"><img src="documentation/responsiveness/404-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/404-tablet.png"><img src="documentation/responsiveness/404-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/404-desktop.png"><img src="documentation/responsiveness/404-desktop.png" width="140" alt="screenshot"></a> |

No overflow, broken layout or unreadable text at any of the three
widths on the pages above.

Dashboard pages, tested locally (an authenticated session against the
deployed site wasn't available for this pass) with the real owner
account and content:

| Section | Mobile | Tablet | Desktop |
| ------- | ------ | ------ | ------- |
| Dashboard — Collections | <a href="documentation/responsiveness/dashboard-mobile.png"><img src="documentation/responsiveness/dashboard-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/dashboard-tablet.png"><img src="documentation/responsiveness/dashboard-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/dashboard-desktop.png"><img src="documentation/responsiveness/dashboard-desktop.png" width="140" alt="screenshot"></a> |
| Dashboard — Collection page | <a href="documentation/responsiveness/dashboard-collection-page-mobile.png"><img src="documentation/responsiveness/dashboard-collection-page-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/dashboard-collection-page-tablet.png"><img src="documentation/responsiveness/dashboard-collection-page-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/dashboard-collection-page-desktop.png"><img src="documentation/responsiveness/dashboard-collection-page-desktop.png" width="140" alt="screenshot"></a> |
| Dashboard — All Artworks | <a href="documentation/responsiveness/dashboard-all-artworks-mobile.png"><img src="documentation/responsiveness/dashboard-all-artworks-mobile.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/dashboard-all-artworks-tablet.png"><img src="documentation/responsiveness/dashboard-all-artworks-tablet.png" width="140" alt="screenshot"></a> | <a href="documentation/responsiveness/dashboard-all-artworks-desktop.png"><img src="documentation/responsiveness/dashboard-all-artworks-desktop.png" width="140" alt="screenshot"></a> |

The sidebar collapses to a hamburger menu below 860px (as designed —
see [dashboard.js](static/js/dashboard.js)); no overflow or broken
layout at any of the three widths.

---

## Browser Compatibility

Tested manually against the deployed site on macOS.

| Section | Chrome | Firefox | Safari |
| ------- | ------ | ------- | ------ |
| Public gallery home | <a href="documentation/browsers/chrome-home.png"><img src="documentation/browsers/chrome-home.png" width="140" alt="screenshot"></a> | <a href="documentation/browsers/firefox-home.png"><img src="documentation/browsers/firefox-home.png" width="140" alt="screenshot"></a> | <a href="documentation/browsers/safari-home.png"><img src="documentation/browsers/safari-home.png" width="140" alt="screenshot"></a> |
| Dashboard (All Artworks) | <a href="documentation/browsers/chrome-dashboard.png"><img src="documentation/browsers/chrome-dashboard.png" width="140" alt="screenshot"></a> | <a href="documentation/browsers/firefox-dashboard.png"><img src="documentation/browsers/firefox-dashboard.png" width="140" alt="screenshot"></a> | <a href="documentation/browsers/safari-dashboard.png"><img src="documentation/browsers/safari-dashboard.png" width="140" alt="screenshot"></a> |

No visual or functional differences across the three browsers.

---

## Lighthouse Audit

Run with the [Lighthouse CLI](https://github.com/GoogleChrome/lighthouse)
against the deployed site.

| Page | Performance | Accessibility | Best Practices | SEO |
| ---- | ----------- | -------------- | --------------- | --- |
| Public gallery home — Mobile | 69 | 95 | 96 | 91 |
| Public gallery home — Desktop | 69 | 95 | 96 | 91 |

![Lighthouse — desktop](documentation/lighthouse/home-desktop.png)
![Lighthouse — mobile](documentation/lighthouse/home-mobile.png)

Accessibility, Best Practices and SEO are all strong. Performance is
held down by Largest Contentful Paint (8.9s desktop / 15.7s mobile),
driven by the unoptimised artwork image files (Lighthouse estimates
~12MB of possible savings) plus the Render free-tier cold start — see
[Known Issues](#known-issues). Not a regression to fix under deadline
pressure; noted here for a future image-optimisation pass (responsive
`srcset`/WebP via Cloudinary's own transformation URLs).

Dashboard pages sit behind a login, which Lighthouse can't provide by
URL alone. They were audited locally instead (same as the dashboard
responsiveness screenshots above): the Lighthouse CLI was given an
authenticated session cookie for the real owner account via
`--extra-headers`, and each report was checked to confirm it audited
the dashboard page itself rather than the login redirect.

| Page | Performance | Accessibility | Best Practices | SEO |
| ---- | ----------- | -------------- | --------------- | --- |
| Dashboard — Collections — Mobile | 74 | 96 | 96 | 91 |
| Dashboard — Collections — Desktop | 76 | 96 | 96 | 91 |
| Dashboard — Collection page — Mobile | 75 | 96 | 96 | 91 |
| Dashboard — Collection page — Desktop | 78 | 96 | 96 | 91 |
| Dashboard — All Artworks — Mobile | 75 | 96 | 96 | 91 |
| Dashboard — All Artworks — Desktop | 77 | 96 | 96 | 91 |

![Lighthouse — dashboard, desktop](documentation/lighthouse/dashboard-desktop.png)
![Lighthouse — dashboard, mobile](documentation/lighthouse/dashboard-mobile.png)

What held each score back:

- **Performance:** Largest Contentful Paint again, from full-size
  artwork images served by Django's local development server with no
  caching headers. This is the same image-optimisation issue as the
  public pages, not something specific to the dashboard.
- **Accessibility:** colour contrast. The dashboard has its own muted
  text tone (`#9a9588`, used for sidebar labels, breadcrumbs and
  artwork subtitles). It measures 2.5–2.8:1 against the dashboard
  backgrounds, below the 4.5:1 WCAG AA minimum. The accent colour used
  for eyebrow labels and the active sidebar link (`#9c6b2c`) measures
  3.8–4.2:1. The public site's muted colour was already fixed for the
  same reason (see [Fixed Bugs](#fixed-bugs)), but the dashboard's
  separate token wasn't.
- **Best Practices:** one console error, a 404 for `/favicon.ico`,
  because the site doesn't declare a favicon.
- **SEO:** no `<meta name="description">`. This matters little on
  owner-only pages that search engines can never reach anyway.

---

## Defensive Programming

Manual and automated testing of input validation, permissions and
error handling.

| Feature | Expectation | Test | Result |
| ------- | ----------- | ---- | ------ |
| Dashboard access | Anonymous visitors cannot reach owner-only pages | Requested `/dashboard/` while logged out | Redirected to login (verified by automated test + manual check) |
| Collection edit (permission) | A user cannot edit another user's Collection | Logged in as a second user, requested the edit URL of another owner's Collection | 404 Not Found, not a permission page (avoids leaking that the resource exists) — verified by automated test |
| Artwork delete (permission) | A user cannot delete another user's Artwork | Logged in as a second user, requested the delete URL of another owner's Artwork | 404 Not Found; Artwork remained in the database — verified by automated test |
| Draft visibility | Draft Collections are never publicly visible | Requested a `draft` Collection's detail URL directly, and checked it's absent from the public list | 404 on direct access, absent from listing — verified by automated test |
| Required field validation | Collection cannot be created without a title | Submitted the create form with an empty `title` | Form redisplayed with "This field is required.", no record created — verified by automated test |
| CSRF protection | Forms reject requests without a valid CSRF token | Django's `CsrfViewMiddleware` is active project-wide (enabled by default, not disabled anywhere in `settings.py`) | Enforced framework-wide |
| Production error visibility | Stack traces are not exposed to visitors | Checked `DEBUG` on the deployed site | `DEBUG=False` in production; generic error pages only |
| Required field validation (Artwork) | Artwork cannot be created without a title | Submitted the create form with an empty `title` | Form redisplayed with "This field is required.", no record created — verified by automated test `test_blank_title_does_not_create_artwork` |
| Navigation | Back/forward buttons never break the site | Checked every custom JS file (`dashboard.js`, `exhibition.js`, `site-menu.js`) for anything that could interfere with browser history — `history.pushState`/`replaceState`, `popstate`, `beforeunload`, a service worker, or a `<base>` tag | None found. All navigation is plain server-rendered page loads via `<a href>`/`window.location.href`; `exhibition.js` only *reads* `location.hash` once (line 439) and never writes it. Nothing overrides default browser history behaviour |
| Commented-out code | Final code is free of commented-out/dead code (assessment 4.2) | Searched every custom Python, JS and template file for disabled code (`# `/`// `/`{# #}` followed by code-like tokens) | None found — every match was a genuine explanatory comment |

---

## User Story Testing

| Target | Expectation | Result | Screenshot |
| ------ | ----------- | ------ | ---------- |
| As the site owner | Sign up and log in securely | Achieved — verified on the deployed site | <a href="documentation/responsiveness/login-desktop.png"><img src="documentation/responsiveness/login-desktop.png" width="140" alt="screenshot"></a> |
| As the site owner | Create a Collection | Achieved — covered by automated test `test_create_collection` | <a href="documentation/validation/html/dashboard-collection-form.png"><img src="documentation/validation/html/dashboard-collection-form.png" width="140" alt="screenshot"></a> |
| As the site owner | Edit or delete a Collection | Achieved — covered by automated tests `test_update_collection`, `test_delete_collection_cascades_to_artworks` | <a href="documentation/validation/html/dashboard-collection-confirm-delete.png"><img src="documentation/validation/html/dashboard-collection-confirm-delete.png" width="140" alt="screenshot"></a> |
| As the site owner | Add an Artwork to a Collection | Achieved — covered by automated test `test_create_artwork`; manually confirmed on the deployed site (created, appeared in the Collection) | <a href="documentation/validation/html/dashboard-artwork-form.png"><img src="documentation/validation/html/dashboard-artwork-form.png" width="140" alt="screenshot"></a> |
| As the site owner | Edit or delete an Artwork | Achieved — covered by automated tests `test_update_artwork`, `test_delete_artwork`; manually confirmed on the deployed site (deleted, disappeared from the list) | <a href="documentation/validation/html/dashboard-artwork-confirm-delete.png"><img src="documentation/validation/html/dashboard-artwork-confirm-delete.png" width="140" alt="screenshot"></a> |
| As a visitor | Browse public Collections | Achieved — only `published` Collections listed, verified by automated test | <a href="documentation/responsiveness/collections-desktop.png"><img src="documentation/responsiveness/collections-desktop.png" width="140" alt="screenshot"></a> |
| As a visitor | View an Artwork's detail | Achieved — manually confirmed: the test Artwork appeared on the public gallery once its Collection was published | <a href="documentation/responsiveness/artwork-detail-desktop.png"><img src="documentation/responsiveness/artwork-detail-desktop.png" width="140" alt="screenshot"></a> |
| As a visitor | Use the site on any device | Achieved — see [Responsiveness](#responsiveness) | <a href="documentation/responsiveness/dashboard-mobile.png"><img src="documentation/responsiveness/dashboard-mobile.png" width="140" alt="screenshot"></a> |

---

## Bugs

### Fixed Bugs

* **`DEBUG=True` live in production** — found while re-checking the 404
  page for the testing docs: the deployed site was rendering Django's
  technical debug error page (stack traces, full settings, the
  complete URLconf pattern list) on 404s instead of the custom
  `404.html`, meaning any real 500 would have exposed the same
  internal detail to visitors. The `DEBUG` environment variable on
  Render had been set to `True`. Fixed by setting it back to `False`
  and redeploying; verified against a fresh (non-cached) URL that the
  custom error pages render correctly again.

* **File uploads broken after adding WhiteNoise (`STORAGES` misconfiguration)** — while seeding local test data, saving an `Artwork` image raised `InvalidStorageError: Could not find config for 'default' in settings.STORAGES`. Defining a custom `STORAGES` dict for WhiteNoise's static file backend had overwritten Django's default file storage entry entirely, since `STORAGES` replaces the whole setting rather than extending it. Fixed by adding an explicit `'default'` entry (`django.core.files.storage.FileSystemStorage`) alongside `'staticfiles'`.

* **Production site returned 400 Bad Request after first deploy** — immediately after the first Render deploy, every request to the live URL returned `400 Bad Request`. A typo in the `ALLOWED_HOSTS` environment variable on Render meant the production hostname didn't match, so Django's `DisallowedHost` protection rejected all requests. Fixed by correcting the `ALLOWED_HOSTS` value on Render and redeploying.

* **Uploaded images returned 404 in production** — the first real Collection cover image uploaded on the live site was saved successfully but the resulting `/media/...` URL 404'd. Django's `urls.py` only serves media files when `DEBUG=True`; in production `DEBUG=False` (correctly), so no route existed to serve them. Worse, Render's filesystem is wiped on every deploy, so even serving them locally-on-disk would not have persisted uploads long-term. Fixed by integrating Cloudinary (`django-cloudinary-storage`) as the media storage backend in production, switched on automatically when Cloudinary credentials are present in the environment; local development is unaffected and continues saving to disk.

* **Automated tests failed after adding the logo image (`Missing staticfiles manifest entry`)** — after referencing `images/logo.svg` in a template, `python manage.py test` started failing with a `ValueError` from WhiteNoise's manifest static storage. The static files manifest (`staticfiles/staticfiles.json`) is only regenerated by `collectstatic`, and had gone stale after the new asset was added. Fixed by re-running `collectstatic` locally; this runs automatically as part of the Render build command in production, so it does not affect deployment.

* **`CLOUDINARY_URL` misconfiguration caused two separate failures in production** — first, `ValueError: Invalid CLOUDINARY_URL scheme`, because the Render environment variable's value had been pasted including the `CLOUDINARY_URL=` prefix instead of just the `cloudinary://...` value. After fixing that, uploads then failed with `cloudinary.exceptions.AuthorizationRequired: Invalid Signature`, traced to a manual `urlparse()`-based parsing of `CLOUDINARY_URL` into a `CLOUDINARY_STORAGE` dict — `urlparse().hostname` lowercases its result, among other subtle mismatches, producing credentials that didn't match Cloudinary's records. Fixed by removing the manual parsing entirely and letting the `cloudinary` package's own built-in `CLOUDINARY_URL` environment parsing configure it, which is what its documentation actually recommends. Diagnosed with the help of the `LOGGING` config added just above, which surfaces full tracebacks for 500 errors in Render's log stream. (The project has since moved on from `CLOUDINARY_URL` entirely — see `raigonos/settings.py`, which now reads `CLOUDINARY_CLOUD_NAME`/`CLOUDINARY_API_KEY`/`CLOUDINARY_API_SECRET` as three separate environment variables, specifically to avoid copy-paste corruption of one long credential string like this bug did.)

* **Muted text colour failed WCAG AA contrast** — a manual contrast-ratio check of the colour palette (script computing relative luminance per the WCAG formula) found `--color-muted` (`#8a8578`, used for eyebrow labels, metadata and footer text) at only 3.35:1 against the page background — below the 4.5:1 minimum for normal-sized text. Fixed by darkening it to `#6b6657` (5.22:1), re-verified with the same script; visually still reads as a muted secondary tone.

### Unfixed Bugs

None known at this time.

### Known Issues

| Issue | Notes |
| ----- | ----- |
| Cold start delay on first request | The Render free-tier Web Service spins down after inactivity; the first request after idle can take 30–50 seconds while it wakes up. This is a hosting-plan limitation, not an application bug. |
| Production database expires 2026-10-09 | Render's free PostgreSQL plan is deleted 90 days after creation. Decision: upgrade to a paid plan before that date (tracked outside this repo, not yet actioned). |
| Lighthouse Performance score (69) | Held down by Largest Contentful Paint on unoptimised artwork images and the Render free-tier cold start, not a code defect. A future pass would serve responsive/WebP images via Cloudinary's transformation URLs. |

---

No critical issues remain outstanding at this stage of development.
