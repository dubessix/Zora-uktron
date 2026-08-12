"""
Ultron Unit & Integration Testing Suite — Phase 7 Refactored Diagnostics
Tests input schema validations, confirmation gates, standard ToolResult formats,
context builders, SQLite audit logs, and timeout handlers.
"""

import unittest
import os
from pathlib import Path

from backend.app.tools.tool_registry import ToolRegistry
from backend.app.tools.context_builder import ToolContextBuilder
from backend.app.database.db import get_db_connection

TEST_FILE = Path(__file__).resolve().parent / "test_phase7_temp_file.txt"

class TestPhase7ToolSystemArchitecture(unittest.IsolatedAsyncioTestCase):
    
    @classmethod
    def setUpClass(cls):
        """Prepare clean SQLite schemas on setup."""
        # Wipes existing audit records to prevent state bleeding
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS tool_audit_logs;")
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        """Clean up temporary test files after runs."""
        if TEST_FILE.exists():
            try:
                TEST_FILE.unlink()
            except OSError:
                pass

    async def test_pydantic_schema_validation(self):
        """Test 1: Verify that incorrect argument types throw clear Pydantic failures."""
        registry = ToolRegistry()
        
        # Missing required field 'content' inside FileWriteArgs
        invalid_args = {"filepath": str(TEST_FILE)}
        response = await registry.execute_tool("file_write", invalid_args)
        
        self.assertFalse(response["success"])
        self.assertIn("validation", response["error"])

    async def test_security_confirmation_gate(self):
        """Test 2: Verify that Level 2/3 tools trigger PENDING_CONFIRMATION intercepts."""
        registry = ToolRegistry()
        
        args = {"command": "echo Hello_World"}
        
        # Dispatch execution without confirmation
        response_1 = await registry.execute_tool("terminal_run", args, has_confirmed=False)
        self.assertEqual(response_1["status"], "PENDING_CONFIRMATION")
        self.assertEqual(response_1["tool_id"], "terminal_run")
        
        # Dispatch execution WITH explicit confirmation; must execute successfully
        response_2 = await registry.execute_tool("terminal_run", args, has_confirmed=True)
        self.assertTrue(response_2["success"])
        self.assertEqual(response_2["data"]["exit_code"], 0)
        self.assertIn("Hello_World", response_2["data"]["stdout"])

    async def test_standard_tool_result_format(self):
        """Test 3: Verify that every executed tool returns the exact, required standard JSON model."""
        registry = ToolRegistry()
        
        test_content = "Standard Result Verification."
        write_args = {"filepath": str(TEST_FILE), "content": test_content}
        
        response = await registry.execute_tool("file_write", write_args)
        
        # Assert exact standard format presence (Requirement 4)
        self.assertIn("success", response)
        self.assertIn("data", response)
        self.assertIn("error", response)
        self.assertIn("metadata", response)
        
        self.assertTrue(response["success"])
        self.assertEqual(response["metadata"]["tool_name"], "File Writer")
        self.assertGreaterEqual(response["metadata"]["execution_time_ms"], 0)

    def test_tool_context_builder_filtering(self):
        """Test 4: Verify that the context builder filters relevant tools based on user prompt tags."""
        registry = ToolRegistry()
        builder = ToolContextBuilder()
        
        all_tools = registry.get_all_tools()
        
        # Query 1: Prompt asking about reading a file (should filter FileReadTool)
        relevant_a = builder.filter_relevant_tools("load my config file", all_tools)
        tool_ids_a = [t.id for t in relevant_a]
        self.assertIn("file_read", tool_ids_a)
        
        # Query 2: Prompt asking about command runs (should filter TerminalRunTool)
        relevant_b = builder.filter_relevant_tools("run the server compiler", all_tools)
        tool_ids_b = [t.id for t in relevant_b]
        self.assertIn("terminal_run", tool_ids_b)
        
        # Query 3: Generic conversational prompt (should return 0 tools to save prompt tokens)
        relevant_c = builder.filter_relevant_tools("hi there, good morning!", all_tools)
        self.assertEqual(len(relevant_c), 0)

    async def test_tool_audit_logs_writes(self):
        """Test 5: Verify that tool executions are recorded in the persistent SQLite audit table."""
        registry = ToolRegistry()
        
        test_content = "Audit log row write test."
        write_args = {"filepath": str(TEST_FILE), "content": test_content}
        
        # Run execution
        await registry.execute_tool("file_write", write_args, session_id="test_sess_7")
        
        # Verify SQLite row creation (Requirement 6)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tool_audit_logs WHERE session_id = ?;", ("test_sess_7",))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row["tool_name"], "File Writer")
            self.assertTrue(row["success"])
            self.assertIn("test_phase7_temp_file.txt", row["arguments"])

    async def test_execution_timeout_handlers(self):
        """Test 6: Verify that long-running commands successfully abort under configured timeouts."""
        registry = ToolRegistry()
        
        # Command runs for 5 seconds, but we set timeout to 0.1 seconds
        args = {"command": "sleep 5" if os.name != "nt" else "timeout 5"}
        
        response = await registry.execute_tool(
            "terminal_run",
            args,
            has_confirmed=True,
            timeout=0.1,
            max_retries=0
        )
        
        self.assertFalse(response["success"])
        self.assertIn("TimeoutError", response["error"])

if __name__ == "__main__":
    unittest.main()
