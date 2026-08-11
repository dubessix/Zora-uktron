# Ultron V1: Unified 6-Tiered Memory Architecture Manual
*Document Version: 1.0.0 — Memory Architecture Reference Manual*

This document provides a highly detailed, professional engineering manual of the unified memory subsystem of **Ultron V1**.

---

## 1. The 6-Tiered Memory Layers

Ultron V1 operates a single, cohesive, shared memory subsystem across six distinct layers, ensuring absolute context durability while matching our strict **8GB RAM constraints**:

```
                              ULTRON MEMORY SYSTEM
                                       │
         ┌──────────────┬──────────────┼──────────────┬──────────────┐
         ▼              ▼              ▼              ▼              ▼
     Short-Term     Persistent      Project        Episodic       Semantic
    (RAM Deque)    (SQLite KV)    (SQLite Config) (SQL Vector)   (SQL Vector)
```

1.  **Short-Term Context RAM (`short_term.py`)**:
    *   *Storage*: In-Memory Deque.
    *   *Scope*: Limited to exactly **50 turns** to prevent memory leaks.
2.  **Persistent User Memory (`persistent_memory.py`)**:
    *   *Storage*: SQLite table `persistent_metadata`.
    *   *Scope*: Permanent configurations about you (e.g. your name, preferences).
3.  **Project State Memory (`project_memory.py`)**:
    *   *Storage*: SQLite table `project_metadata`.
    *   *Scope*: Project goals, notes, and active configurations.
4.  **Episodic Memory (`episodic_memory.py`)**:
    *   *Storage*: SQLite table `vector_memories` (type: `"episodic"`).
    *   *Scope*: Timestamped vector recordings of past occurrences.
5.  **Semantic Memory (`semantic_memory.py`)**:
    *   *Storage*: SQLite table `vector_memories` (type: `"semantic"`).
    *   *Scope*: Vector recordings of technical knowledge.
6.  **Emotional Memory (`emotional_memory.py`)**:
    *   *Storage*: SQLite table `vector_memories` (type: `"emotional"`).
    *   *Scope*: Vector recordings of past stress states.

---

## 2. Low-RAM Hybrid Vector Database Architecture

Rather than running heavy local neural models on your 8GB PC, we implement an incredibly fast, zero-local-memory **Hybrid SQLite + NumPy Vector Store**:

### A. SQLite Table: `vector_memories`
```sql
CREATE TABLE IF NOT EXISTS vector_memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,         -- episodic | semantic | emotional
    content TEXT NOT NULL,
    embedding BLOB NOT NULL,     -- NumPy float32 array serialized
    metadata TEXT DEFAULT '{}',  -- JSON formatted meta variables (personality, etc.)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### B. High-Speed Local NumPy Cosine Similarity
Vector arrays are serialized directly as float32 binary BLOBs. Search queries invoke **local NumPy linear-algebra operations**:
*   *Algorithm*:
    $$\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|}$$
*   This matches similar states in **sub-10ms** and consumes **0MB of static local memory**.

### C. Duplicate Write Prevention Check
Before saving any vector, we query the top match. If similarity exceeds the configured threshold in `config.yaml` (`duplicate_similarity_threshold: 0.95`), the write transaction is aborted, protecting database health.

---

## 3. Decoupled SOLID Cache Policy Engine

To prevent dynamic personal context (like Todo lists or Git states) from returning stale, cached completions, we implement a decoupled **Cache Policy Engine**:

*   **`BaseCachePolicy`**: An abstract interface contract.
*   **`HeuristicKeywordCachePolicy` (V1)**: Evaluates prompts. If a query contains dynamic keys (like *todo*, *git*, *reminder*), it flags `cache_skip = True`, instructing `LLMRouter` to bypass the cache completely and pull real-time database state.
*   **V2 Upgrade**: Allows easy, zero-router-modification transition to AI/Intent-based classifications (Refer to `docs/adr_001_intelligent_cache_policy.md`).
