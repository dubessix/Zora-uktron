# Ultron V1: Software Testing & Isolated Verification Strategy
*Document Version: 1.0.2 — Sprints 0-7 QA manual*

This document provides a highly detailed, professional engineering manual of our testing architecture and quality assurance parameters.

---

## 1. Automated Phased Diagnostic Tests

Consistent with our strict developer directive (**"Build First, Verify Later"**), every phase in our roadmap includes a dedicated, isolated test suite under the `tests/` directory.

All tests utilize Python's standard `unittest` and `unittest.IsolatedAsyncioTestCase` frameworks, meaning **zero external database locks or live internet connections are required** to verify the entire code base.

```
                             TESTS COMPILATION REGISTRY
+-----------------------------------------------------------------------------------------+
| FILE NAME          | TYPE         | RESPONSIBILITY                                      |
+--------------------+--------------+-----------------------------------------------------+
| `test_phase1.py`   | Integration  | Relational databases, WAL locks, history queries    |
| `test_phase2.py`   | Mock E2E     | LRU Cache hits, key rotations on 429 errors         |
| `test_phase3.py`   | Unit         | Short term deques, persistent KVs, config states    |
| `test_phase4.py`   | Integration  | Intents, confidence heuristics, speed tracks        |
| `test_phase5.py`   | Unit/Math    | NumPy Cosine Similarity math, duplicate prevention  |
| `test_phase6.py`   | Stateful E2E | Extensible Es signals, auto-return lifecycles       |
| `test_phase7.py`   | Integration  | Tool schema validations, confirmation gates,        |
|                    |              | Standard ToolResult, Context Builder, audit logs,   |
|                    |              | and non-blocking execution timeout handler tests.   |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Dynamic Mock-Live Hybrid Architecture

To let you verify the codebase without active Groq or Gemini API keys, the test suites are engineered with a **mock fallback wrapper**:
*   *Key Pool Scan*: The test cases verify whether the keys inside your `.env` are updated.
*   *Default Mock Mode*: If no active keys are found, the tests automatically mock HTTPX client responses, returning mock payloads while successfully logging state changes.
*   *Live verification*: If active keys are present, the test suites will naturally connect to cloud endpoints, testing genuine internet latency.

---

## 3. How to Execute Diagnostic Suites

When your development machine is restored, open your Linux Ubuntu (or Windows 11) terminal and execute the following commands in sequence:

### A. Activate the copied Virtual Environment
```bash
cd /home/user
source venv/bin/activate
```

### B. Run Individual Test Files
```bash
# Verify database operations & schemas (Phase 1)
./venv/bin/python -m unittest tests/test_phase1.py

# Verify key rotation & caching (Phase 2)
./venv/bin/python -m unittest tests/test_phase2.py

# Verify persistent profile memory (Phase 3)
./venv/bin/python -m unittest tests/test_phase3.py

# Verify Cognitive speed track routing (Phase 4)
./venv/bin/python -m unittest tests/test_phase4.py

# Verify NumPy Cosine Similarity & Gate (Phase 5)
./venv/bin/python -m unittest tests/test_phase5.py

# Verify extensible stress scores & auto-return lifecycle (Phase 6)
./venv/bin/python -m unittest tests/test_phase6.py

# Verify tool validation, permissions and security gates (Phase 7)
./venv/bin/python -m unittest tests/test_phase7.py
```

### C. Run the Consolidated Quality Assurance Audit
To run all test cases concurrently and verify complete backward compatibility:
```bash
./venv/bin/python -m unittest discover -s tests -p "test_*.py"
```
*Expected Output*: `Ran 30 tests. OK.`
