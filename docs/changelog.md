# Changelog

## Personal V1 repair series (2026-08-15)

### Phase 0–2

- Isolated all test storage and bounded semantic scans.
- Centralized effective model configuration and provider/model cache identity.
- Enforced allowed paths and exact one-time action confirmations.

### Phase 3–5

- Serialized coding changes and verified atomic writes.
- Hardened terminal process groups, output bounds, and command policy.
- Added URL/DNS/redirect/download controls and honest external-operation status.
- Corrected newest history and project-scoped memory controls.

### Phase 6–8

- Added online backups, retention, integrity/WAL maintenance, restore lock, and rollback.
- Added centralized background task lifecycle.
- Shipped config, launcher, frontend, prompts, and skills in the wheel.
- Replaced daily Vite dev serving with loopback production assets, two health gates, duplicate lock, monitoring, and bounded cleanup.
- Migrated FastAPI lifecycle to lifespan.

### Phase 9

- Removed known fabricated executable telemetry, weather, research/search, notification, Git, and briefing values.
- Added real local universal search and persisted UI personality selection.
- Changed no-key LLM and TTS/provider failures to explicit unavailable states.
- Reworded limited security checks so zero findings is not a safety guarantee.

### Phase 10

- Updated pinned Python and frontend dependencies.
- Added vulnerability, Ruff, Bandit, coverage, wheel-install, and build release gates.
- Replaced obsolete models/endpoints/counts and absolute quality claims in documentation.

Git commit history is the source of truth for exact changes and hashes.
