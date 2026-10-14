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

## Expanded checker validation

The revised course annotations pass with [Teloce checker PR #18](https://github.com/aldanedev-create/teloce-py/pull/18), which supplies the missing runtime contracts and conditional narrowing. It produces zero findings for this project, with 45 API/security tests passing, 14 production components built, and development and production browser workflows passing at desktop/mobile sizes. This does not make Teloce universally type-safe; unsupported dynamic/slot/import cases remain documented in its checker guide.

The checker improvements are not yet a published PyPI release. To reproduce in a separate test environment using the exact tested source:

```bash
python -m pip install "teloce-py[typecheck] @ git+https://github.com/aldanedev-create/teloce-py.git@32d8ee5340f540a3996d21efae9f7c82fcd3657f"
python management.py typecheck
```

The normal course requirements remain on published 0.3.0 packages for runtime use. Their older checker may still report adapter errors; do not claim that the unpublished fixes are included in 0.3.0. The course corrections annotate nullable state, arrays and method parameters, narrow caught errors and event targets, and declare host-owned router/PWA globals. No blanket `any` or diagnostic suppression was added.
