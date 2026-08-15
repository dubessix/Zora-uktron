"""Final release regressions for dependency floors, quality config, and docs."""

from __future__ import annotations

import json
import os
import re
import tomllib
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner


ROOT = Path(__file__).resolve().parent.parent


class TestReleaseDependencies(unittest.TestCase):
    def test_python_requirements_use_audited_versions(self):
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        expected = {
            "fastapi": "0.141.1",
            "python-dotenv": "1.2.2",
            "click": "8.4.2",
            "PyYAML": "6.0.3",
            "pydantic": "2.13.4",
            "httpx": "0.28.1",
            "python-multipart": "0.0.32",
        }
        for package, version in expected.items():
            self.assertRegex(requirements, rf"(?m)^{re.escape(package)}=={re.escape(version)}$")
        for vulnerable in ("fastapi==0.111.1", "python-dotenv==1.0.1", "click==8.1.7"):
            self.assertNotIn(vulnerable, requirements)

    def test_frontend_uses_fixed_vite_and_reproducible_direct_versions(self):
        package = json.loads((ROOT / "frontend" / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["devDependencies"]["vite"], "7.3.6")
        self.assertEqual(package["devDependencies"]["@vitejs/plugin-react"], "5.1.4")
        self.assertEqual(package["dependencies"]["react"], "19.2.8")
        self.assertEqual(package["dependencies"]["react-dom"], "19.2.8")


class TestReleaseQualityConfiguration(unittest.TestCase):
    def test_ruff_and_application_coverage_gates_are_configured(self):
        config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        self.assertIn("F", config["tool"]["ruff"]["lint"]["select"])
        self.assertIn("B", config["tool"]["ruff"]["lint"]["select"])
        self.assertEqual(config["tool"]["coverage"]["report"]["fail_under"], 70)
        self.assertEqual(config["tool"]["coverage"]["run"]["source"], ["backend", "launcher"])

    @unittest.skipIf(os.name == "nt", "POSIX executable bit is not meaningful on Windows")
    def test_linux_launcher_script_is_executable(self):
        self.assertTrue(os.access(ROOT / "start_ultron.sh", os.X_OK))


class TestConsoleLauncherOwnership(unittest.TestCase):
    def test_ultron_start_runs_launcher_in_current_process(self):
        from backend.app import cli

        launcher_main = Mock(return_value=0)
        with patch.object(
            cli.runpy,
            "run_path",
            return_value={"main": launcher_main},
        ) as run_path:
            result = CliRunner().invoke(cli.main, ["start"])
        self.assertEqual(result.exit_code, 0, result.output)
        run_path.assert_called_once()
        launcher_main.assert_called_once_with()


class TestReleaseDocumentation(unittest.TestCase):
    def test_documentation_has_no_retired_models_endpoints_or_absolute_claims(self):
        documents = list(ROOT.glob("*.md")) + list((ROOT / "docs").glob("*.md"))
        combined = "\n".join(path.read_text(encoding="utf-8") for path in documents)
        forbidden = (
            "gemini-1.5-flash",
            "text-embedding-004",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
            "/ws/voice",
            "100% coverage",
            "fully un-mocked",
            "all green",
            "no technical debt",
        )
        for literal in forbidden:
            self.assertNotIn(literal.lower(), combined.lower(), literal)

    def test_readme_states_release_and_hardware_boundaries(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        config = (ROOT / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("Personal V1 release candidate", readme)
        self.assertIn("owner's Windows/browser/microphone/Spotify hardware", readme)
        self.assertIn("gemini-embedding-001", readme)
        self.assertIn("POST /api/speak", readme)
        self.assertIn('status: "personal-v1-release-candidate"', config)
        self.assertNotIn('status: "pre-development"', config)


if __name__ == "__main__":
    unittest.main()
