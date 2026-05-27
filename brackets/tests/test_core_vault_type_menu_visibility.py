#!/usr/bin/env python3
"""Tests de tipo de vault y visibilidad de menú por contexto."""

import os
import sys
import tempfile

import yaml

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.main import BitacoraManager
from brackets.core.menu_engine import MenuEngine


class TestCoreVaultTypeMenuVisibility:
    """Valida reglas work/personal para contexto de menú."""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def _assert(self, condition: bool, message: str):
        if not condition:
            raise AssertionError(message)

    def _write_config(self, vault_dir: str, config: dict):
        os.makedirs(os.path.join(vault_dir, "data"), exist_ok=True)
        with open(os.path.join(vault_dir, "data", "config.yaml"), "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)

    def test_explicit_vault_type_personal_sets_context(self):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self._write_config(
                    tmp,
                    {
                        "version": "1.0.0",
                        "system": "Brackets",
                        "vault_name": "PersonalNotes",
                        "vault_type": "personal",
                        "feature_flags": {"bitacoras_enabled": True},
                        "paths": {"notes_root": ".", "data_dir": "data"},
                    },
                )

                manager = BitacoraManager(tmp)
                context = manager._menu_context()

                self._assert(manager.vault_type == "personal", "Debe respetar vault_type explícito")
                self._assert(context["vault_type_personal"] is True, "Debe activar contexto personal")
                self._assert(context["vault_type_work"] is False, "No debe activar contexto work")

            print("✅ Test: vault_type personal explícito activa contexto correcto")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test explicit_vault_type_personal_sets_context falló: {e}")
            self.failed += 1

    def test_description_personal_fallback_sets_personal(self):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self._write_config(
                    tmp,
                    {
                        "version": "1.0.0",
                        "system": "Brackets",
                        "description": "Notas y bitácoras a nivel personal",
                        "feature_flags": {"bitacoras_enabled": True},
                        "paths": {"notes_root": ".", "data_dir": "data"},
                    },
                )

                manager = BitacoraManager(tmp)

                self._assert(manager.vault_type == "personal", "Descripción personal debe inferir vault personal")

            print("✅ Test: fallback por descripción detecta vault personal")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test description_personal_fallback_sets_personal falló: {e}")
            self.failed += 1

    def test_menu_context_tag_hides_pomodoro_for_personal(self):
        try:
            config = {
                "menus": {
                    "tools": {
                        "items": [
                            {
                                "id": "pomodoro",
                                "label": "Pomodoro Timer",
                                "keys": ["p"],
                                "action": "exec",
                                "command": "tool_pomodoro",
                                "context_tag": "vault_type_work",
                            },
                            {
                                "id": "emoji",
                                "label": "Emoji",
                                "keys": ["e"],
                                "action": "exec",
                                "command": "tool_emoji",
                            },
                        ]
                    }
                }
            }
            menu_engine = MenuEngine(vault_root=".", fallback_config=config)
            menu_engine.config = config

            personal_items = menu_engine.visible_items(
                "tools",
                {
                    "vault_type_work": False,
                    "vault_type_personal": True,
                },
            )
            work_items = menu_engine.visible_items(
                "tools",
                {
                    "vault_type_work": True,
                    "vault_type_personal": False,
                },
            )

            personal_commands = {item.get("command") for item in personal_items}
            work_commands = {item.get("command") for item in work_items}

            self._assert("tool_pomodoro" not in personal_commands, "Pomodoro debe ocultarse en vault personal")
            self._assert("tool_pomodoro" in work_commands, "Pomodoro debe verse en vault work")
            self._assert("tool_emoji" in personal_commands, "Items sin context_tag deben seguir visibles")

            print("✅ Test: context_tag filtra pomodoro según tipo de vault")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test menu_context_tag_hides_pomodoro_for_personal falló: {e}")
            self.failed += 1

    def run_all(self):
        print("\n🧪 TESTS: core/vault_type_menu_visibility.py")
        print("=" * 50)

        self.test_explicit_vault_type_personal_sets_context()
        self.test_description_personal_fallback_sets_personal()
        self.test_menu_context_tag_hides_pomodoro_for_personal()

        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestCoreVaultTypeMenuVisibility()
    success = tester.run_all()
    sys.exit(0 if success else 1)
