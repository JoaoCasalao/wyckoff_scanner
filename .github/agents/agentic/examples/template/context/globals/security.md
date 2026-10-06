<!-- ════════════════════════════════════════════════════════════════════════════
  TEMPLATE — broadly reusable. The checklist and principles are language-agnostic — keep
  them. The examples are Python; adapt them and the scanner command to your stack.

  FILL-IN CHECKLIST:
   [ ] Static security scanner — your language's scanner command
   [ ] (Optional) swap the Python examples for your language

  Delete the comments when done.
═════════════════════════════════════════════════════════════════════════════ -->

# Security Rules

Read this before writing or editing any code, regardless of language.

## Mandatory checks before every commit

- [ ] No hardcoded secrets (API keys, passwords, tokens, private keys, cloud credentials)
- [ ] All user inputs validated at entry points
- [ ] Injection prevention — parameterised queries for SQL; list-args (never a shell string) for subprocesses
- [ ] No `eval()` / `exec()` (or your language's equivalent) on untrusted input
- [ ] No unsafe deserialisation of untrusted data (`yaml.load`, `pickle`, etc.) — use the safe variant
- [ ] No path traversal (validate paths, reject `..`)
- [ ] Authentication / authorisation verified on every endpoint
- [ ] Error messages don't leak internal details or PII
- [ ] No PII in logs, test fixtures, or output files

## Secret management

```python
# GOOD — fails fast if the secret is missing
api_key = os.environ["API_KEY"]

# BAD — silently None, hard to debug, easy to ship broken
api_key = os.environ.get("API_KEY")
```

Never hardcode secrets. Use environment variables or a secrets manager. (Adapt the example to your language.)

## Injection / subprocess safety

```python
# GOOD — list args, no shell interpretation
subprocess.run(["tool", "-i", input_path, output_path], check=True)

# BAD — shell=True with interpolated input is command injection
subprocess.run(f"tool -i {input_path}", shell=True)
```

The same principle applies to SQL (parameterise, never string-concatenate user input) and to any other
interpreter you hand a string.

## Static security scanning
<!-- >>> FILL IN: your language's security scanner. -->
```bash
<security scanner>   # e.g. bandit -r src/  |  npm audit  |  gosec ./...
```

## Security response protocol

If a security issue is found:
1. **STOP** — do not continue with unrelated work.
2. Fix CRITICAL issues before any commit.
3. Rotate any secrets that may have been exposed.
4. Review the rest of the codebase for similar patterns.
