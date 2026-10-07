# Dependency provenance

- Flaxon base: `Flaxon-Labs/flaxon` commit `403d571eb6e35ac7a24fb9972fb2d3e3ccb19e62`.
- Framework security patch commit: `f25954b` in the supplied patch (local commit).
- Flaxon course wheel: `0.2.6+course.1`, with the patch applied and the version
  module updated to preserve a valid numeric version-info tuple.
- Teloce-Py: `aldanedev-create/teloce-py` commit `10f786b9ce99cf62cb2e154a913843b027b20ee7`, built as `0.2.6`.
- MinifyJS: official package pinned to `0.1.3`.

`checksums.json` records SHA-256 values for both wheels. Verify with
`python scripts/verify_vendor.py`. Framework/Teloce MIT license notices are
included in their distribution files; source repositories provide the full
history. These course wheels have not been uploaded to PyPI or released upstream.

The local framework version makes this patch distinguishable from official
`flaxon==0.2.6`. Use the course requirements when reproducing the recordings.
