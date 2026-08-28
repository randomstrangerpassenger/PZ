# Iris Build Import and Execution Contract

Status: current link-only projection

The current package/import owner is `Iris/tooling/src/iris_tooling/**`. Build and validation command literals are owned only by `Iris/build/ENTRYPOINTS.md`.

Current rules:

- package code receives repository context explicitly and does not infer it from installation path or current working directory;
- build outputs and validation evidence use caller-supplied repository-external roots;
- `Iris/build/tools/common/**` is a compatibility adapter surface for retained root pipelines;
- `Iris/build/description/v2/tools/build/**` is historical/reproduction space and must not be imported or executed as current authority;
- validation membership, applicability, and verdict remain in `Iris/validation`;
- planning and implementation start from `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`; the static route index remains a machine projection.

Historical Phase 1–Round 3 execution details remain available in Git history and the `_docs` historical records. They are not restated here because this document is not a second command or authority owner.
