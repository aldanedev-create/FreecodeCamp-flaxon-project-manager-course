# Runnable course checkpoints

These are four real states, not fifteen tags pointing to the finished app.
Intermediate chapters use the book's file references and exercises.

| Chapter | Branch on GitHub | Local tag / bundle | Scope |
|---|---|---|---|
| 01 | starter-scoped-css | chapter-01-scoped-setup | Prepared welcome application with scoped component CSS and pinned dependencies |
| 04 | chapter-04-auth | chapter-04-auth | Auth-only backend, /api/me, ten test cases |
| 07 | backend-ready | chapter-07-backend | Complete APIs and backend tests |
| 15 | main | course-scoped-css-v2 | Completed scoped-CSS SPA, Admin/CMS and instructor recording guide |

## Choose a version without losing your edits

Commit or stash your work, then use a separate worktree:

```bash
git fetch origin
git worktree add ../course-starter origin/starter-scoped-css
git worktree add ../course-auth origin/chapter-04-auth
git worktree add ../course-complete origin/main
```

The prepared starter includes pinned course dependencies and vendor wheels. Its
Teloce styles live in scoped component blocks. The raw `flaxon new` output and
historical `chapter-01-setup` branch/tag still preserve the unadapted generator;
chapter 1 explains the scoped-CSS adaptation. The old chapter-15-complete tag
preserves the first edition. New versions use new tag names rather than moving
existing checkpoints. Keep starter and finished code in separate directories.

The auth checkpoint already contains the shared migration schema, including
later project/task tables; only auth routes and /api/me are mounted. Its tests
exercise authentication, validation, session revocation, body limits, and startup
configuration. Staff/CMS and the customer SPA are not enabled there.

The delivered Git bundle preserves the actual local checkpoint tags. Remote
checkpoint branches are available through the connected GitHub app. That app has
no exposed tag-creation operation, and terminal authentication is unavailable in
this session, so remote tags must be published from your signed-in terminal.

## Publish genuine tags from the remote checkpoints

From a fresh clone (or rename any conflicting local tags first):

```bash
git fetch origin
git tag -a chapter-01-scoped-setup origin/starter-scoped-css -m "Chapter 01: scoped CSS starter"
git tag -a chapter-04-auth origin/chapter-04-auth -m "Chapter 04: authentication backend"
git tag -a chapter-07-backend origin/backend-ready -m "Chapter 07: backend ready"
git tag -a course-scoped-css-v2 origin/main -m "Scoped CSS course and instructor guide v2"
git push origin chapter-01-scoped-setup chapter-04-auth chapter-07-backend course-scoped-css-v2
```

Do not overwrite an existing remote tag. These names describe checkpoint scope;
the backend checkpoint contains later-domain source as a reference and the book
teaches features in order. Add finer snapshots after rehearsing your video.
