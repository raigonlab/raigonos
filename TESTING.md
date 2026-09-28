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
| Collections | https://raigonos.onrender.com/collections/ | 0 errors, 0 warnings | [collections.png](documentation/validation/html/collections.png) |
| Collection detail | https://raigonos.onrender.com/collection/flow-lines/ | 0 errors, 0 warnings | [collection-detail.png](documentation/validation/html/collection-detail.png) |
| Artwork detail | https://raigonos.onrender.com/artwork/25/ | 0 errors, 0 warnings | [artwork-detail.png](documentation/validation/html/artwork-detail.png) |

🚧 Dashboard pages (require login) will be validated via "Validate by
Direct Input" and added here.

### CSS

Validated with the
[W3C Jigsaw CSS Validator](https://jigsaw.w3.org/css-validator/)
against the deployed stylesheet.

| File | Result |
| ---- | ------ |
| `static/css/style.css` | Valid CSS3. 0 errors, 1 warning (`-apple-system` flagged as a vendor extension — expected and harmless, used intentionally as part of the system-font fallback stack) |

### JavaScript

Linted with [JSHint](https://jshint.com) (`v2.13.6`, run via `npx jshint`)
against every custom JS file:

```bash
npx jshint static/js/dashboard.js static/js/exhibition.js static/js/site-menu.js
```

| File | Result |
| ---- | ------ |
| `static/js/dashboard.js` | 0 errors, 0 warnings |
| `static/js/exhibition.js` | 0 errors, 0 warnings |
| `static/js/site-menu.js` | 0 errors, 0 warnings |

![JSHint run, exit code 0](documentation/validation/jshint-terminal.png)

---

## Responsiveness

🚧 To be tested manually across mobile, tablet and desktop breakpoints
using browser dev tools, with screenshots saved to
`documentation/responsiveness/`.

| Section | Mobile | Tablet | Desktop | Notes |
| ------- | ------ | ------ | ------- | ----- |
| Public gallery home | | | | |
| Collection detail | | | | |
| Artwork detail | | | | |
| Dashboard | | | | |
| Login / Signup | | | | |

---

## Browser Compatibility

🚧 To be tested manually across major browsers, with screenshots saved
to `documentation/browsers/`.

| Section | Chrome | Firefox | Safari | Notes |
| ------- | ------ | ------- | ------ | ----- |
| Public gallery home | | | | |
| Dashboard / CRUD forms | | | | |

---

## Lighthouse Audit

🚧 To be run via Chrome DevTools against the deployed site, with
screenshots saved to `documentation/lighthouse/`.

| Page | Mobile | Desktop |
| ---- | ------ | ------- |
| Public gallery home | | |
| Dashboard | | |

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

| Target | Expectation | Result |
| ------ | ----------- | ------ |
| As the site owner | Sign up and log in securely | Achieved — verified on the deployed site |
| As the site owner | Create a Collection | Achieved — covered by automated test `test_create_collection` |
| As the site owner | Edit or delete a Collection | Achieved — covered by automated tests `test_update_collection`, `test_delete_collection_cascades_to_artworks` |
| As the site owner | Add an Artwork to a Collection | Achieved — covered by automated test `test_create_artwork`; 🚧 manual browser confirmation pending |
| As the site owner | Edit or delete an Artwork | Achieved — covered by automated tests `test_update_artwork`, `test_delete_artwork`; 🚧 manual browser confirmation pending |
| As a visitor | Browse public Collections | Achieved — only `published` Collections listed, verified by automated test |
| As a visitor | View an Artwork's detail | Achieved — 🚧 manual browser confirmation pending |
| As a visitor | Use the site on any device | 🚧 Pending manual responsiveness testing |

---

## Bugs

### Fixed Bugs

* **File uploads broken after adding WhiteNoise (`STORAGES` misconfiguration)** — while seeding local test data, saving an `Artwork` image raised `InvalidStorageError: Could not find config for 'default' in settings.STORAGES`. Defining a custom `STORAGES` dict for WhiteNoise's static file backend had overwritten Django's default file storage entry entirely, since `STORAGES` replaces the whole setting rather than extending it. Fixed by adding an explicit `'default'` entry (`django.core.files.storage.FileSystemStorage`) alongside `'staticfiles'`.

* **Production site returned 400 Bad Request after first deploy** — immediately after the first Render deploy, every request to the live URL returned `400 Bad Request`. A typo in the `ALLOWED_HOSTS` environment variable on Render meant the production hostname didn't match, so Django's `DisallowedHost` protection rejected all requests. Fixed by correcting the `ALLOWED_HOSTS` value on Render and redeploying.

* **Uploaded images returned 404 in production** — the first real Collection cover image uploaded on the live site was saved successfully but the resulting `/media/...` URL 404'd. Django's `urls.py` only serves media files when `DEBUG=True`; in production `DEBUG=False` (correctly), so no route existed to serve them. Worse, Render's filesystem is wiped on every deploy, so even serving them locally-on-disk would not have persisted uploads long-term. Fixed by integrating Cloudinary (`django-cloudinary-storage`) as the media storage backend in production, switched on automatically when a `CLOUDINARY_URL` environment variable is present; local development is unaffected and continues saving to disk.

* **Automated tests failed after adding the logo image (`Missing staticfiles manifest entry`)** — after referencing `images/logo.svg` in a template, `python manage.py test` started failing with a `ValueError` from WhiteNoise's manifest static storage. The static files manifest (`staticfiles/staticfiles.json`) is only regenerated by `collectstatic`, and had gone stale after the new asset was added. Fixed by re-running `collectstatic` locally; this runs automatically as part of the Render build command in production, so it does not affect deployment.

* **`CLOUDINARY_URL` misconfiguration caused two separate failures in production** — first, `ValueError: Invalid CLOUDINARY_URL scheme`, because the Render environment variable's value had been pasted including the `CLOUDINARY_URL=` prefix instead of just the `cloudinary://...` value. After fixing that, uploads then failed with `cloudinary.exceptions.AuthorizationRequired: Invalid Signature`, traced to a manual `urlparse()`-based parsing of `CLOUDINARY_URL` into a `CLOUDINARY_STORAGE` dict — `urlparse().hostname` lowercases its result, among other subtle mismatches, producing credentials that didn't match Cloudinary's records. Fixed by removing the manual parsing entirely and letting the `cloudinary` package's own built-in `CLOUDINARY_URL` environment parsing configure it, which is what its documentation actually recommends. Diagnosed with the help of the `LOGGING` config added just above, which surfaces full tracebacks for 500 errors in Render's log stream.

* **Muted text colour failed WCAG AA contrast** — a manual contrast-ratio check of the colour palette (script computing relative luminance per the WCAG formula) found `--color-muted` (`#8a8578`, used for eyebrow labels, metadata and footer text) at only 3.35:1 against the page background — below the 4.5:1 minimum for normal-sized text. Fixed by darkening it to `#6b6657` (5.22:1), re-verified with the same script; visually still reads as a muted secondary tone.

### Unfixed Bugs

None known at this time.

### Known Issues

| Issue | Notes |
| ----- | ----- |
| Cold start delay on first request | The Render free-tier Web Service spins down after inactivity; the first request after idle can take 30–50 seconds while it wakes up. This is a hosting-plan limitation, not an application bug. |

---

No critical issues remain outstanding at this stage of development.
