<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — broadly reusable. The PRINCIPLES are language-agnostic — keep them. The
  EXAMPLES are Python; if your project isn't Python, swap them for idiomatic ones in your
  language. Tune the numeric limits to your team (the defaults are sensible, not laws).

  FILL-IN CHECKLIST (all tagged >>> FILL IN below):
   [ ] Language standards — your style guide, type-annotation expectations, formatter/linter
   [ ] Docstrings — your doc-comment convention
   [ ] Tooling commands — your exact format / lint / typecheck / test commands
   [ ] (Optional) swap the Python examples for your language; tune the limits

  Delete the comments when done.
═════════════════════════════════════════════════════════════════════════════ -->

# Coding Style

Read this before writing or editing any application code.

## Function design (single responsibility)

**One function does one thing.** If you need "and" to describe what a function does, split it.

```python
# BAD — loads AND filters AND transforms in one function
def process(source, key):
    data = load(source)
    data = [d for d in data if d.key == key]
    return [transform(d) for d in data]

# GOOD — each function has a single responsibility
def load_data(source): ...
def filter_by_key(data, key): ...
def transform_all(data): ...
```

Rules (tune the limits to your team):
- Functions must be **small** (a good default: under ~50 lines). If you are approaching the limit, extract a helper.
- Functions must have **one level of abstraction** — don't mix high-level orchestration with low-level detail in the same function.
- Prefer many small, named functions over inline lambdas or long chains that need a comment to explain them.
- A function that builds a result should not also log, validate, and persist it — separate those concerns.

## Immutability

Prefer creating new objects over mutating existing ones, especially shared state.

```python
# GOOD
result = {**existing, "new_key": value}
updated = [*items, new_item]

# BAD
existing["new_key"] = value
items.append(new_item)  # mutating a shared list
```

Prefer immutable data structures for config and DTOs (in Python, `@dataclass(frozen=True)`; use the
equivalent in your language).

## File organisation
- A few hundred lines per file is typical; set a hard ceiling your team agrees on (e.g. 800).
- Many small, focused files over few large files.
- High cohesion, low coupling.
- Organise by domain/feature, not by type.

## Error handling
- Handle errors explicitly at every level.
- Never silently swallow exceptions.
- Log detailed context internally, return user-friendly messages at boundaries.

```python
# GOOD
try:
    result = process(data)
except ValueError as e:
    logger.error("Invalid data for %s: %s", path, e)
    raise ProcessingError(f"Cannot process {path}") from e

# BAD
try:
    result = process(data)
except Exception:
    pass
```

## Input validation
- Validate all external inputs at system boundaries (CLI args, file paths, request payloads, API responses).
- Fail fast with clear error messages.
- Never trust external data.

## Language standards
<!-- >>> FILL IN for your language: style guide (PEP 8 / Google / Airbnb / gofmt / ...),
     type-annotation expectations, and the formatter+linter you standardise on. -->
- Follow your language's standard style guide.
- Use static types on public signatures where the language supports them.
- Standardise on one formatter and one linter; run them via the pre-commit hook, not by hand mid-task.

## Anti-patterns to avoid
<!-- These are Python examples; replace with your language's equivalents. -->
- Type checks via `type(obj) == X` → use `isinstance(obj, X)`.
- `value == None` → use `value is None`.
- Wildcard imports (`from module import *`).
- Bare `except: pass`.
- Mutable default arguments (`def f(items=[])`) → default to `None` and assign inside.
- Unsafe deserialisation (`yaml.load`, `pickle` on untrusted data) → use the safe variant.
- `print()` in production code → use a logger.

## Docstrings / doc comments
<!-- >>> FILL IN: pick a docstring/doc-comment convention for your language. -->
Use a consistent convention (e.g. Google-style docstrings in Python). Every public function gets one.
Include an example whenever the behaviour is non-obvious. Self-explanatory private helpers don't need one.

## Code quality checklist
- [ ] Functions within the size limit
- [ ] Files within the size limit
- [ ] No deep nesting (> 4 levels) — use early returns
- [ ] No hardcoded values — use constants or config
- [ ] No `print()` / stray debug output — use a logger
- [ ] Immutable patterns used where it matters (no mutation of shared state)

## Tooling commands
<!-- >>> FILL IN: the exact format / lint / typecheck / test commands for your project. -->
```bash
<format command>      # e.g. ruff format .  |  prettier --write .  |  gofmt -w .
<lint command>        # e.g. ruff check .   |  eslint .            |  golangci-lint run
<typecheck command>   # e.g. mypy .         |  tsc --noEmit
<test command>        # e.g. pytest         |  npm test           |  go test ./...
```
