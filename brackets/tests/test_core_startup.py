#!/usr/bin/env python3
"""Tests para orquestación de arranque CLI en core/startup.py."""

import os
import sys
from types import SimpleNamespace

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.core.startup import run_startup_flow


class _FakeManager:
    def __init__(self, vault_directory: str):
        self.vault_directory = vault_directory
        self.run_called = False

    def run(self):
        self.run_called = True


class TestCoreStartup:
    """Valida flujo parseado -> selección vault -> dispatch -> run."""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def _assert(self, condition: bool, message: str):
        if not condition:
            raise AssertionError(message)

    def _args(self, directory=None):
        return SimpleNamespace(directory=directory)

    def test_early_exit_code(self):
        try:
            called = {"manager": False, "dispatch": False}

            def _manager_factory(_vault):
                called["manager"] = True
                return _FakeManager(_vault)

            def _dispatch(_args, _manager, _vault):
                called["dispatch"] = True
                return None

            exit_code = run_startup_flow(
                args=self._args(),
                current_dir=".",
                manager_factory=_manager_factory,
                has_action_flags_fn=lambda _a: False,
                select_vault_directory_fn=lambda **_kwargs: (None, 0),
                dispatch_cli_action_fn=_dispatch,
            )

            self._assert(exit_code == 0, "Debe propagar early_exit_code")
            self._assert(called["manager"] is False, "No debe crear manager en salida temprana")
            self._assert(called["dispatch"] is False, "No debe ejecutar dispatch en salida temprana")

            print("✅ Test: early exit corta el flujo")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test early_exit_code falló: {e}")
            self.failed += 1

    def test_dispatch_exit_code(self):
        try:
            state = {"vault": None, "run": False}

            def _manager_factory(vault):
                state["vault"] = vault
                return _FakeManager(vault)

            def _dispatch(_args, manager, _vault):
                state["run"] = manager.run_called
                return 1

            exit_code = run_startup_flow(
                args=self._args(),
                current_dir=".",
                manager_factory=_manager_factory,
                has_action_flags_fn=lambda _a: True,
                select_vault_directory_fn=lambda **_kwargs: (".", None),
                dispatch_cli_action_fn=_dispatch,
            )

            self._assert(exit_code == 1, "Debe propagar código del dispatcher")
            self._assert(state["vault"] == ".", "Debe crear manager con vault resuelto")
            self._assert(state["run"] is False, "No debe ejecutar modo interactivo si dispatch devuelve código")

            print("✅ Test: dispatch con exit code evita run()")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test dispatch_exit_code falló: {e}")
            self.failed += 1

    def test_interactive_run_when_no_dispatch_code(self):
        try:
            holder = {"manager": None}

            def _manager_factory(vault):
                manager = _FakeManager(vault)
                holder["manager"] = manager
                return manager

            exit_code = run_startup_flow(
                args=self._args(),
                current_dir=".",
                manager_factory=_manager_factory,
                has_action_flags_fn=lambda _a: False,
                select_vault_directory_fn=lambda **_kwargs: ("vault-path", None),
                dispatch_cli_action_fn=lambda _args, _manager, _vault: None,
            )

            self._assert(exit_code is None, "Modo interactivo debe devolver None")
            self._assert(holder["manager"] is not None, "Debe crear manager")
            self._assert(holder["manager"].run_called is True, "Debe ejecutar run() en modo interactivo")

            print("✅ Test: sin exit code se ejecuta run()")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test interactive_run_when_no_dispatch_code falló: {e}")
            self.failed += 1

    def run_all(self):
        print("\n🧪 TESTS: core/startup.py")
        print("=" * 50)

        self.test_early_exit_code()
        self.test_dispatch_exit_code()
        self.test_interactive_run_when_no_dispatch_code()

        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestCoreStartup()
    success = tester.run_all()
    sys.exit(0 if success else 1)
