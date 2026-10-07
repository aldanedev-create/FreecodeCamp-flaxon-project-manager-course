# Runnable course checkpoints

These are four real states, not fifteen tags pointing to the finished app.
Intermediate chapters use the book's file references and exercises.

| Chapter | Branch on GitHub | Local tag / bundle | Scope |
|---|---|---|---|
| 01 | chapter-01-setup | chapter-01-setup | Original generated welcome application |
| 04 | chapter-04-auth | chapter-04-auth | Auth-only backend, /api/me, ten test cases |
| 07 | backend-ready | chapter-07-backend | Complete APIs and backend tests |
| 15 | main | chapter-15-complete | Completed SPA, Admin/CMS, book and deployment guides |

## Choose a version without losing your edits

Commit or stash your work, then use a separate worktree:

```bash
git fetch origin
git worktree add ../course-starter origin/chapter-01-setup
git worktree add ../course-auth origin/chapter-04-auth
git worktree add ../course-complete origin/main
```

The original starter has generic generated dependencies. Install the course's
pinned dependencies from the completed checkout first, then use that activated
Python environment while running the starter. The starter ZIP additionally
includes vendor wheels and pinned requirements copied from the completed course.
Keep generated code and finished code in separate directories.

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
git tag -a chapter-01-setup origin/chapter-01-setup -m "Chapter 01: generated starter"
git tag -a chapter-04-auth origin/chapter-04-auth -m "Chapter 04: authentication backend"
git tag -a chapter-07-backend origin/backend-ready -m "Chapter 07: backend ready"
git tag -a chapter-15-complete origin/main -m "Chapter 15: complete course"
git push origin chapter-01-setup chapter-04-auth chapter-07-backend chapter-15-complete
```

Do not overwrite an existing remote tag. These names describe checkpoint scope;
the backend checkpoint contains later-domain source as a reference and the book
teaches features in order. Add finer snapshots after rehearsing your video.
