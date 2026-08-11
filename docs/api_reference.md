# Ultron V1: REST API Reference Manual
*Document Version: 1.0.2 — REST API Interface with Security & ToolResult Schemas*

This document provides a highly precise, technical specification of all HTTP endpoints exposed by the Ultron V1 FastAPI backend, incorporating the newly created Phase 7 security confirmation payloads and standardized ToolResult structures.

---

## 1. System Health Endpoint

### `GET /api/health`
Retrieves backend operational health, uptime, system resource metrics, and execution environment variables.

*   **Request Headers**: None.
*   **Response Payload Schema (JSON)**:
    ```json
    {
      "status": "healthy",
      "uptime_seconds": 14.52,
      "system_metrics": {
        "memory_rss_mb": 28.42,
        "cpu_percent": 0.0,
        "total_system_ram_usage_percent": 54.2
      },
      "environment": {
        "os_platform": "Linux",
        "os_release": "6.8.0-1008-aws",
        "python_version": "3.13.1"
      }
    }
    ```
*   **HTTP Status Codes**:
    *   `200 OK`: Successful verification.

---

## 2. Conversation Chat Gate Endpoint

### `POST /api/chat`
Accepts user prompts, processes the 7-step Cognitive pipeline, manages automatic stress state switches, writes log records to SQLite, and returns completions.

*   **Request Headers**:
    *   `Content-Type: application/json`
*   **Request Payload Schema (JSON)**:
    ```json
    {
      "session_id": "test_sess_refactored",  // Optional. Generates UUIDv4 if null.
      "content": "What is my name?"          // Required. Min length: 1.
    }
    ```
*   **Response Payload Schema (Standard Completion)**:
    ```json
    {
      "id": "e67dfb6a-91a1-43b6-9ca1-ee928a6f3b0e",
      "session_id": "test_sess_refactored",
      "content": "Received and saved in context. Echoing: 'What is my name?'",
      "personality": "ultron",
      "response_ms": 2
    }
    ```

---

## 3. Tool Confirmation Intercept (Phase 7 Security Payload)
When the Cognitive Orchestrator attempts to execute a Level 2 or Level 3 tool (like terminal shell scripts or deletions) without explicit confirmation, the routing API intercepts the transaction and returns a `PENDING_CONFIRMATION` JSON body to trigger a client-side glassmorphic confirmation popup.

*   **Response Payload Schema (Pending Confirmation)**:
    ```json
    {
      "status": "PENDING_CONFIRMATION",
      "tool_id": "terminal_run",
      "message": "Tool 'terminal_run' requires manual confirmation for execution.",
      "required_permission_level": 2
    }
    ```

---

## 4. Standard ToolResult Schema (Phase 7 Output Model)
Every tool executed under the `ToolRegistry` returns the exact same, standardized JSON response structure to prevent formatting bugs across different tools:

*   **Response Payload Schema (Standardized ToolResult)**:
    ```json
    {
      "success": true,
      "data": {
        "exit_code": 0,
        "stdout": "Hello_World",
        "stderr": ""
      },
      "error": null,
      "metadata": {
        "execution_time_ms": 12,
        "tool_name": "Terminal Runner"
      }
    }
    ```

*   **HTTP Status Codes**:
    *   `200 OK`: Successful transaction (whether standard completion, security intercept, or tool execution).
    *   `422 Unprocessable Entity`: Input validation error.
    *   `500 Internal Server Error`: Server connection dropped.

---

## 5. Session Dialogue History Endpoint

### `GET /api/history`
Loads the chronological history logs belonging to a specific session.

*   **Request Parameters (Query)**:
    *   `session_id` (string, required): Unique session UUID.
*   **Request Headers**: None.
*   **Response Payload Schema (JSON)**:
    ```json
    [
      {
        "id": "e67dfb6a-91a1-43b6-9ca1-ee928a6f3b0e",
        "session_id": "test_sess_refactored",
        "timestamp": "2026-07-31T01:14:02.123567",
        "user_message": "What is my name?",
        "ai_response": "Received and saved in context. Echoing: 'What is my name?'",
        "personality": "ultron",
        "tools_used": [],
        "widget_shown": null,
        "intent": "Conversation",
        "mode": "developer",
        "path_used": "fast",
        "response_ms": 2
      }
    ]
    ```
*   **HTTP Status Codes**:
    *   `200 OK`: Successful retrieval.
    *   `400 Bad Request`: Missing query string parameter.
    *   `500 Internal Server Error`: SQLite reading error.
