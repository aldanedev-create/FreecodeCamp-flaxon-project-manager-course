# Course repository

The course source is available at:
https://github.com/aldanedev-create/FreecodeCamp-flaxon-project-manager-course

```bash
git clone https://github.com/aldanedev-create/FreecodeCamp-flaxon-project-manager-course.git
cd FreecodeCamp-flaxon-project-manager-course
```

Follow the root README for installation. Chapter checkpoints are available as
branches: `chapter-01-setup`, `backend-ready`, and `course-v1`.
Use `git switch backend-ready` to inspect the completed backend.

The original development history and checkpoint tags are also preserved in the
separately delivered Git bundle. Terminal publication requires signing in with
your normal Git credential manager; never commit access tokens.

## Upstream framework patch

`vendor/flaxon-cms-security.patch` is a separately reviewable framework patch.
Apply it to the recorded Flaxon revision in a clean framework checkout:

```bash
git switch -c fix/cms-course-authorization 403d571eb6e35ac7a24fb9972fb2d3e3ccb19e62
git am /absolute/path/to/flaxon-cms-security.patch
```

Run the new security regression tests and existing Admin/CMS tests before opening
a framework PR. The course wheel already contains these fixes, so installing the
course does not depend on merging or releasing the framework patch.
