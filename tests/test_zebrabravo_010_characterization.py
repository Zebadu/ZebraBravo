"""Characterisation tests for the active ZebraBravo 0.1.0 implementation.

These tests intentionally record current behaviour, including behaviours that
may be improved during a later refactor.  They use temporary memory stores and
never read or alter the project's real memory or log files.
"""

import io
import json
import shutil
import subprocess
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULES_DIR = PROJECT_ROOT / "modules"
sys.path.insert(0, str(MODULES_DIR))

from assistant import Assistant  # noqa: E402
from memory_manager import MemoryManager  # noqa: E402


VALID_TYPES = {
    "fact",
    "preference",
    "person",
    "project",
    "event",
    "instruction",
}


def empty_memory():
    return {"memories": [], "next_id": 1}


def populated_memory():
    return {
        "memories": [
            {
                "id": 1,
                "type": "fact",
                "created": "2026-08-12 23:33:27",
                "content": "Zeb likes motorcycles.",
            },
            {
                "id": 3,
                "type": "project",
                "created": "2026-08-13 13:11:29",
                "content": "ZebraBravo is in initial construction.",
            },
        ],
        "next_id": 5,
    }


class MemoryTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        (self.project_root / "Memory").mkdir()
        self.manager = MemoryManager(self.project_root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_memory(self, memory):
        with self.manager.memory_file.open("w", encoding="utf-8") as file:
            json.dump(memory, file)

    def read_memory(self):
        with self.manager.memory_file.open(encoding="utf-8") as file:
            return json.load(file)


class MemoryManagerValidationTests(MemoryTestCase):
    def test_loads_current_legacy_format_with_id_gap(self):
        memory = populated_memory()
        self.write_memory(memory)
        self.assertEqual(self.manager.load(), memory)

    def test_valid_types_are_accepted(self):
        memory = empty_memory()
        memory["memories"] = [
            {"id": index, "type": memory_type, "created": "", "content": "x"}
            for index, memory_type in enumerate(sorted(VALID_TYPES), start=1)
        ]
        self.manager.validate_memory(memory)

    def test_root_must_be_object(self):
        with self.assertRaisesRegex(ValueError, "Memory file must contain a JSON object"):
            self.manager.validate_memory([])

    def test_required_top_level_fields_are_validated(self):
        with self.assertRaisesRegex(ValueError, "missing the 'memories' field"):
            self.manager.validate_memory({"next_id": 1})
        with self.assertRaisesRegex(ValueError, "missing the 'next_id' field"):
            self.manager.validate_memory({"memories": []})

    def test_top_level_field_types_are_validated(self):
        with self.assertRaisesRegex(ValueError, "'memories' must be a list"):
            self.manager.validate_memory({"memories": {}, "next_id": 1})
        with self.assertRaisesRegex(ValueError, "'next_id' must be an integer"):
            self.manager.validate_memory({"memories": [], "next_id": "1"})

    def test_memory_entry_and_required_fields_are_validated(self):
        with self.assertRaisesRegex(ValueError, "Each memory must be a JSON object"):
            self.manager.validate_memory({"memories": ["not an object"], "next_id": 1})
        with self.assertRaisesRegex(ValueError, "Memory is missing fields: content, created, type"):
            self.manager.validate_memory({"memories": [{"id": 1}], "next_id": 2})

    def test_memory_field_types_and_type_value_are_validated(self):
        base = {"id": 1, "type": "fact", "created": "", "content": "text"}
        invalid_id = dict(base, id="1")
        with self.assertRaisesRegex(ValueError, "Memory ID must be an integer"):
            self.manager.validate_memory({"memories": [invalid_id], "next_id": 2})
        invalid_type = dict(base, type="note")
        with self.assertRaisesRegex(ValueError, "Invalid memory type: note"):
            self.manager.validate_memory({"memories": [invalid_type], "next_id": 2})
        invalid_content = dict(base, content=1)
        with self.assertRaisesRegex(ValueError, "Memory content must be text"):
            self.manager.validate_memory({"memories": [invalid_content], "next_id": 2})

    def test_current_validator_allows_extra_fields_and_unchecked_metadata(self):
        memory = {
            "memories": [
                {"id": 1, "type": "fact", "created": None, "content": "", "extra": True},
                {"id": 1, "type": "fact", "created": "not a date", "content": "duplicate id"},
            ],
            "next_id": 1,
            "schema_version": 99,
        }
        self.manager.validate_memory(memory)

    def test_load_propagates_missing_file_and_invalid_json_errors(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.load()
        self.manager.memory_file.write_text("{", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            self.manager.load()


class MemoryManagerCrudTests(MemoryTestCase):
    def setUp(self):
        super().setUp()
        self.write_memory(populated_memory())

    def test_add_uses_next_id_preserves_gaps_and_increments_id(self):
        self.manager.add_memory("New note")
        memory = self.read_memory()
        self.assertEqual([item["id"] for item in memory["memories"]], [1, 3, 5])
        self.assertEqual(memory["next_id"], 6)
        added = memory["memories"][-1]
        self.assertEqual(added["type"], "fact")
        self.assertEqual(added["content"], "New note")
        self.assertRegex(added["created"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_add_accepts_each_supported_type_and_rejects_unsupported_type(self):
        for memory_type in VALID_TYPES:
            self.manager.add_memory(memory_type, memory_type)
        self.assertEqual({item["type"] for item in self.read_memory()["memories"][-6:]}, VALID_TYPES)
        with self.assertRaisesRegex(ValueError, "Invalid memory type: note"):
            self.manager.add_memory("x", "note")

    def test_search_is_case_insensitive_content_substring_search_in_file_order(self):
        self.assertEqual([item["id"] for item in self.manager.search("ZEB")], [1, 3])
        self.assertEqual(self.manager.search("instruction"), [])
        self.assertEqual([item["id"] for item in self.manager.search("")], [1, 3])

    def test_get_by_id_returns_first_match_or_none(self):
        self.assertEqual(self.manager.get_by_id(3)["content"], "ZebraBravo is in initial construction.")
        self.assertIsNone(self.manager.get_by_id(99))

    def test_update_changes_first_match_and_persists(self):
        self.assertTrue(self.manager.update_memory(3, "Updated"))
        self.assertEqual(self.manager.get_by_id(3)["content"], "Updated")
        self.assertFalse(self.manager.update_memory(99, "No change"))

    def test_delete_removes_memory_without_reusing_id(self):
        self.assertTrue(self.manager.delete_memory(1))
        self.assertEqual([item["id"] for item in self.manager.load()["memories"]], [3])
        self.assertEqual(self.manager.load()["next_id"], 5)
        self.assertFalse(self.manager.delete_memory(99))

    def test_save_validates_before_overwriting_existing_file(self):
        original = self.read_memory()
        with self.assertRaisesRegex(ValueError, "'next_id' must be an integer"):
            self.manager.save({"memories": [], "next_id": "bad"})
        self.assertEqual(self.read_memory(), original)


class ActiveAssistantCommandTests(MemoryTestCase):
    def setUp(self):
        super().setUp()
        self.write_memory(populated_memory())
        self.assistant = Assistant(self.project_root)

    def run_command(self, command):
        output = io.StringIO()
        with redirect_stdout(output):
            result = self.assistant.process_command(command)
        return result, output.getvalue()

    def test_exit_and_help_are_case_insensitive(self):
        result, output = self.run_command("EXIT")
        self.assertFalse(result)
        self.assertEqual(output, "Goodbye, Zeb.\n")
        result, output = self.run_command("HeLp")
        self.assertTrue(result)
        self.assertIn("  remember <text>  - Save a new memory\n", output)
        self.assertIn("  exit             - Exit ZebraBravo\n", output)

    def test_remember_uses_fact_type_and_keeps_all_text_after_command(self):
        result, output = self.run_command("remember project Plan refactor")
        self.assertTrue(result)
        self.assertEqual(output, "Memory saved.\n")
        added = self.read_memory()["memories"][-1]
        self.assertEqual(added["type"], "fact")
        self.assertEqual(added["content"], "project Plan refactor")

    def test_search_show_and_delete_commands(self):
        result, output = self.run_command("search ZEB")
        self.assertTrue(result)
        self.assertEqual(output, "Found 2 memory(s).\n[1] Zeb likes motorcycles.\n[3] ZebraBravo is in initial construction.\n")
        result, output = self.run_command("show 3")
        self.assertTrue(result)
        self.assertEqual(output, "ID: 3\nType: project\nCreated: 2026-08-13 13:11:29\nContent: ZebraBravo is in initial construction.\n")
        result, output = self.run_command("delete 3")
        self.assertTrue(result)
        self.assertEqual(output, "Memory deleted.\n")
        self.assertIsNone(self.assistant.memory_manager.get_by_id(3))

    def test_invalid_ids_have_current_messages(self):
        cases = {
            "show nope": "Please provide a valid memory ID.\n",
            "delete nope": "Please provide a valid memory ID.\n",
        }
        for command, expected in cases.items():
            with self.subTest(command=command):
                result, output = self.run_command(command)
                self.assertTrue(result)
                self.assertEqual(output, expected)

    def test_unknown_and_command_without_trailing_space_are_unknown(self):
        for command in ("nonsense", "remember", "remember ", "search", "search ", "show", "delete"):
            with self.subTest(command=command):
                result, output = self.run_command(command)
                self.assertTrue(result)
                self.assertEqual(output, "Unknown command. Type 'help' for available commands.\n")

    def test_blank_command_returns_none_currently(self):
        result, output = self.run_command("   ")
        self.assertIsNone(result)
        self.assertEqual(output, "")


class CoreMainStartupIntegrationTests(unittest.TestCase):
    """Run the current entry point only against a disposable project copy."""

    def test_startup_banner_log_append_and_exit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            for directory in ("core", "modules", "config", "memory"):
                (project_root / directory).mkdir()

            for relative_path in (
                "core/main.py",
                "modules/assistant.py",
                "modules/json_memory_repository.py",
                "modules/memory_manager.py",
                "modules/memory_service.py",
                "modules/intent/__init__.py",
                "modules/intent/contracts.py",
                "modules/intent/interpreter.py",
                "modules/intent/executor.py",
                "modules/capabilities/context.py",
                "modules/capabilities/contracts.py",
                "modules/capabilities/executor.py",
                "modules/capabilities/policy.py",
                "modules/capabilities/policy_gateway.py",
                "modules/capabilities/registry.py",
                "modules/capabilities/runtime.py",
                "modules/capabilities/development.py",
                "modules/capabilities/development_protocol.py",
                "modules/capabilities/development_service.py",
                "modules/capabilities/development_transport.py",
                "modules/capabilities/plugins/archive.py",
                "modules/capabilities/plugins/filesystem.py",
                "modules/capabilities/plugins/git.py",
                "modules/capabilities/plugins/truth.py",
                "config/config.json",
            ):
                source = PROJECT_ROOT / relative_path
                destination = project_root / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

            memory = {
                "memories": [
                    {"id": 1, "type": "fact", "created": "2026-08-12 23:33:27", "content": "First"},
                    {"id": 3, "type": "project", "created": "2026-08-13 13:11:29", "content": "Second"},
                ],
                "next_id": 5,
            }
            (project_root / "memory" / "memory.json").write_text(
                json.dumps(memory), encoding="utf-8"
            )

            result = subprocess.run(
                [sys.executable, "core/main.py"],
                cwd=project_root,
                input="exit\n",
                text=True,
                capture_output=True,
                timeout=10,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout,
                "ZebraBravo\n"
                "Zoey is online.\n"
                "System initialization successful.\n"
                "Memory loaded: 2 memories.\n\n"
                "Type 'help' for available commands.\n\n"
                "> Goodbye, Zeb.\n",
            )
            self.assertEqual(result.stderr, "")

            log_file = project_root / "logs" / "zebrabravo.log"
            self.assertTrue(log_file.is_file())
            log_lines = log_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(log_lines), 1)
            self.assertRegex(
                log_lines[0],
                r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - ZebraBravo started - Zoey online\.$",
            )


if __name__ == "__main__":
    unittest.main()