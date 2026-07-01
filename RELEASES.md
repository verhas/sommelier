# Release Notes

![Pâtisserie](logo.svg)

---

## v1.1.0 — 2026-07-01

### New features

- **Multi-level defaults** — schema-level `defaults:` and per-job `defaults:` with three-tier priority cascade: `context > job defaults > schema defaults`
- **List-element defaults** — a dict under a defaults key is merged into every item of a matching list in context (e.g. supply a fallback `type` for every field without repeating it on each element)
- **Multiple dict-type defaults keys** — all dict keys in a defaults block are now applied independently in a single pass (previously only the first was applied)
- **Nested dict defaults** — when a defaults value is a dict and the matching context value is also a dict, defaults are merged recursively
- **Template expressions in context values** — any `context:` or `defaults:` value may contain a `{{ }}` Jinja2 expression referencing other context values; pati resolves the whole graph via fixed-point iteration
- **Predefined variables** — ten `__NAME__`-style variables injected automatically into every job context: `__JOB__`, `__TEMPLATE__`, `__DATE__`, `__TIME__`, `__YEAR__`, `__OUTPUT__`, `__OUTPUT_STEM__`, `__OUTPUT_DIR__`, `__OUTPUT_EXT__`, `__PATISSERIE_VERSION__`
- **Circular dependency detection** — when context resolution reaches a dead end, pati raises a `ValueError` listing the unresolvable keys
- **Warning on unused defaults key** — pati warns when a `defaults:` key defines a dict but the matching context key is not a list (likely a misconfiguration)
- **`pati generate` / `pati init` aliases** — English-language aliases for `pati cuire` and `pati mise`
- **Logo** — SVG logo added

### Improvements

- `pati cuire` (`generate`) now supports glob patterns for selective job execution
- `--quiet` / `--silent` / `--verbose` global logging flags
- Skip file writes when generated content is unchanged (avoids touching timestamps)
- `pati mise` (`init`) protects existing files instead of overwriting them
- `__OUTPUT__` available before context resolution so templated output paths resolve correctly; path-derived macros (`__OUTPUT_STEM__` etc.) follow the resolved path

### Packaging

- Removed `setup.py` — `pyproject.toml` is now the sole build configuration
- Fixed deprecated `license = {text = ...}` TOML table → SPDX string `"MIT OR Apache-2.0"`
- Removed deprecated `License ::` PyPI classifiers; license now declared via SPDX expression

---

## v1.0.0 — 2026-07-01

Initial release of **pâtisserie** (`pati`), a language-agnostic boilerplate generator from YAML data models and Jinja2 templates.

### Features

- `pati cuire` — generate files from all jobs defined in `.pati/schema.yaml`
- `pati mise` — initialise project structure (`.pati/schema.yaml` + `.pati/tmplts/`)
- File-based and inline Jinja2 templates
- Template expressions in `output:` path (e.g. `generated/{{ class_name }}.java`)
- YAML anchors and aliases for DRY configuration (`shared:` block)
- `--dry-run` flag
- `--output-dir` override
- `--config / -c` flag to point at a non-default schema file
- Job name glob filtering (`pati cuire 'entity_*'`)
- Example templates bundled: Java Spring, Rust/sqlx, Python SQLAlchemy, Go/GORM
- Package published to PyPI as `patisserie`
