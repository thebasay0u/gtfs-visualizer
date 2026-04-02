# `.agent` to `.agents` Migration

## Canonical Path

The repository canonical planning workspace is now:

- `.agents/`

All new and updated planning artifacts must reference `.agents/*`.

## Temporary Compatibility Window

Legacy local workflows that still call `.agent/*` can use a local filesystem alias:

- Windows setup: `.\scripts\setup-agent-compat.ps1`
- Windows removal: `.\scripts\remove-agent-compat.ps1`

This alias is local-only and is intentionally ignored by git.

## Removal Criteria

Compatibility guidance can be removed when all are true:

1. No active local tooling uses `.agent/*`.
2. CI and local workflow docs have used `.agents/*` for one full milestone cycle.
3. Repository search for `.agent(?!s)` only matches this document and compatibility scripts.

## Verification Commands

Use these checks after any migration follow-up:

```powershell
git grep -nP "\.agent(?!s)"
git grep -n "\.agents"
```
