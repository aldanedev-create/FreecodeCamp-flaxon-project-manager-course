# Type checking the course with Flaxon 0.3.0

Install the published course dependencies using `python -m pip install -r requirements-dev.txt`. The executable project pins Flaxon 0.3.0 and Teloce-Py 0.3.0. Historical book/recovery snapshots may still describe preview wheels; use these package pins when following those chapters on 0.3.0.

## Start the server without automatic checks

Keep `typecheck=False` in the existing `app.use_teloce(...)` call. This disables the background checker on published Flaxon 0.3.0, while keeping compilation, asset reload and the development debugger available. Keep this registration above `if app.is_management: return app` so management commands can discover the UI.

```bash
python management.py runserver
```

When replaying older course chapters or restoring checkpoints, apply that same option to their Teloce registration. Do not add a second `app.use_teloce()` call.

## Check explicitly

```bash
python management.py typecheck
python management.py typecheck --json
```

The course currently reports type errors; these commands are not a passing CI gate for its unchanged components. The switch above does not silence this explicit command or convert failures into successes.

## What the reproduction showed

On the published 0.3.0 packages, starting the original debug server reported 77 diagnostics while `/login` still returned HTTP 200 and Teloce produced JavaScript. After disabling the watcher, the server served the same page without background type diagnostics. Compilation can strip TypeScript types without checking them, so successful compilation alone does not prove type correctness.

There are two classes of findings:

- Course typing issues: unannotated `null` and empty-array state, implicit parameter types, `catch` variables of type `unknown`, and DOM event targets needing narrowing.
- Adapter limitations: Teloce's runtime/compiler supports `$emit`, `beforeUnmount`, and automatically imported signal helpers, but the 0.3.0 type adapter does not fully model them. Some missing-method errors cascade from its incomplete component contract. Generated router globals and template conditional narrowing also need better typing support.

The native TypeScript compiler is checking the generated representation it receives. This evidence identifies limitations in that representation and course annotations; it does not establish a native compiler bug. The runtime and type adapter need separate validation. Keep API tests and production builds, and use the manual checker when reviewing these issues.
