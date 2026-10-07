# Staff Admin, CMS, and application security

## Account boundaries

Application registration creates only a domain user. It never creates an Admin
account. Bootstrap staff interactively with `python management.py setup-admin`.
The Admin uses its own cookie and persistent account store. Enable MFA for the
administrator through the Admin profile before using a real deployment.

The application uses Argon2 password hashes, high-entropy opaque session cookies,
hashed session-token storage, eight-hour server-side expiry, session rotation on
login/registration/logout, HttpOnly cookies, and SameSite=Lax. Production cookies
are Secure. Mutations require JSON, a session-bound CSRF header, and a matching
Origin when the browser supplies one.

`FLAXON_SECRET_KEY` must contain at least 32 random characters in production.
Do not log cookies, passwords, CSRF tokens, or password hashes. Domain responses
never expose hashes. The auth limiter is durable but single-instance; a public
service should additionally enforce IP limits at its trusted ingress.

## Exact staff permissions

`strict_permissions=True` disables legacy broad model permission fallbacks.
Create staff groups through the roles screen and grant only the needed keys.
Built-in group names do not automatically grant access to every custom model.

| Role | Suggested permissions |
|---|---|
| Project reader | `admin.view_dashboard`, `project.view_project`, `task.view_task` |
| Project operator | Above plus `project.change_project`, `task.change_task`; add delete only when necessary |
| Help editor | `admin.view_dashboard`, `help_article.view_help_article`, `help_article.add_help_article`, `help_article.change_help_article` |
| Help publisher | Editor permissions plus `cms.publish_content`, `cms.restore_revision` |
| Administrator | `admin.superuser`, reserved for trusted administrators |

The course Admin adapters allow reading, editing, and deleting records. Creating
projects/tasks remains in the user application so ownership is assigned correctly.
Staff with a permitted model capability may access all registered records; this
is not a multi-tenant staff portal. Do not grant these capabilities to customers.

## CMS authorization fixes included in the course build

- CMS without an auth backend denies requests by default.
- Creation, updates, imports, restore, and actions enforce publishing rights.
- Import publication authorization is checked before any row is created.
- Editing already published content also requires publishing rights.
- Restoring requires the model change and revision-restore capabilities.
- CMS mutations retain the Admin CSRF requirement.

The compatibility option `allow_unauthenticated=True` is for isolated demos only;
the course never enables it. Custom CMS actions conservatively require publisher
rights because their callbacks may alter publication state.

Rich-text CMS fields are sanitized by the installed nh3 integration. `v-html` is
used only with this sanitized published content. Public routes whitelist returned
fields and exclude drafts, revision history, tokens, and Admin credentials.

Mail delivery, passkey verification, antivirus scanning, and distributed services
are external integrations; this course does not enable or claim those features.
Uploads are outside the main course and requests are limited to 256 KiB.

## Before recording or publishing

Run API and browser tests after dependency changes. Exercise denied requests as
well as happy paths. Review `vendor/flaxon-cms-security.patch` before upstream
integration. This targeted patch and test suite are not a complete security audit.
