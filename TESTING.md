# Testing

> Return back to the [README.md](README.md) file.

---

## Automated Testing

15 automated tests live in `gallery/tests.py`, covering models, public
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
| `DashboardPermissionTests` | Dashboard requires login; a user cannot edit or delete another user's Collection/Artwork (404, not just hidden) |
| `CollectionCrudTests` | Create/update/delete via the dashboard forms; blank required field is rejected; deleting a Collection cascades to its Artworks |

**Result:** 15/15 passing.

```
Ran 15 tests in 4.024s

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

| Page | URL checked | Result |
| ---- | ----------- | ------ |
| Public gallery home | https://raigonos.onrender.com/ | 0 errors, 0 warnings |
| Login | https://raigonos.onrender.com/accounts/login/ | 0 errors, 0 warnings |
| Signup | https://raigonos.onrender.com/accounts/signup/ | 0 errors, 0 warnings |

🚧 Collection detail, Artwork detail and Dashboard pages will be
re-validated once real content exists to render them against.

### CSS

Validated with the
[W3C Jigsaw CSS Validator](https://jigsaw.w3.org/css-validator/)
against the deployed stylesheet.

| File | Result |
| ---- | ------ |
| `static/css/style.css` | Valid CSS3. 0 errors, 1 warning (`-apple-system` flagged as a vendor extension — expected and harmless, used intentionally as part of the system-font fallback stack) |

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
| 🚧 Empty form fields (Artwork) | Same required-field protection applies to Artwork | | |
| 🚧 Navigation | Back/forward buttons never break the site | | |

---

## User Story Testing

| Target | Expectation | Result |
| ------ | ----------- | ------ |
| As the site owner | Sign up and log in securely | Achieved — verified on the deployed site |
| As the site owner | Create a Collection | Achieved — covered by automated test `test_create_collection` |
| As the site owner | Edit or delete a Collection | Achieved — covered by automated tests `test_update_collection`, `test_delete_collection_cascades_to_artworks` |
| As the site owner | Add an Artwork to a Collection | Achieved — CRUD view implemented; 🚧 manual browser confirmation pending |
| As the site owner | Edit or delete an Artwork | Achieved — CRUD view implemented; 🚧 manual browser confirmation pending |
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

### Unfixed Bugs

None known at this time.

### Known Issues

| Issue | Notes |
| ----- | ----- |
| Cold start delay on first request | The Render free-tier Web Service spins down after inactivity; the first request after idle can take 30–50 seconds while it wakes up. This is a hosting-plan limitation, not an application bug. |

---

No critical issues remain outstanding at this stage of development.
