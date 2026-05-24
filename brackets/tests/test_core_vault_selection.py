#!/usr/bin/env python3
"""Tests para selección de vault extraída de main.py."""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from brackets.core.vault_selection import select_vault_directory


class _FakeVaultManager:
    def __init__(self, _workspace_root: str, selections):
        self.selections = list(selections)
        self.refresh_called = False

    def show_vault_menu(self):
        return self.selections.pop(0) if self.selections else None

    def refresh_vaults(self):
        self.refresh_called = True


class TestCoreVaultSelection:
    """Valida orquestación de selección de vault en arranque CLI."""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def _assert(self, condition: bool, message: str):
        if not condition:
            raise AssertionError(message)

    def test_directory_arg_passthrough(self):
        try:
            vault, code = select_vault_directory(
                directory_arg="C:/vault",
                has_flags=False,
            )
            self._assert(vault == "C:/vault", "Debe respetar --directory")
            self._assert(code is None, "No debe salir temprano")

            print("✅ Test: respeta directory_arg")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test directory_arg_passthrough falló: {e}")
            self.failed += 1

    def test_flags_without_directory_use_dot(self):
        try:
            vault, code = select_vault_directory(
                directory_arg=None,
                has_flags=True,
            )
            self._assert(vault == ".", "Con flags debe usar directorio actual")
            self._assert(code is None, "No debe salir temprano")

            print("✅ Test: con flags usa '.'")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test flags_without_directory_use_dot falló: {e}")
            self.failed += 1

    def test_local_context_short_circuit(self):
        try:
            vault, code = select_vault_directory(
                directory_arg=None,
                has_flags=False,
                current_dir="/tmp",
                resolve_workspace_context_fn=lambda _cwd: ("/tmp/local-vault", True),
            )
            self._assert(vault == "/tmp/local-vault", "Debe usar vault local detectado")
            self._assert(code is None, "No debe salir temprano")

            print("✅ Test: contexto local evita selector global")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test local_context_short_circuit falló: {e}")
            self.failed += 1

    def test_global_selector_exit(self):
        try:
            manager = _FakeVaultManager("/ws", [None])
            vault, code = select_vault_directory(
                directory_arg=None,
                has_flags=False,
                current_dir="/ws",
                resolve_workspace_context_fn=lambda _cwd: ("/ws", False),
                vault_manager_factory=lambda _root: manager,
                create_new_vault_fn=lambda _root: None,
            )
            self._assert(vault is None, "Al salir no debe devolver vault")
            self._assert(code == 0, "Salir del selector debe devolver código 0")

            print("✅ Test: salida del selector global")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test global_selector_exit falló: {e}")
            self.failed += 1

    def test_global_selector_create_new_success(self):
        try:
            manager = _FakeVaultManager("/ws", ["CREATE_NEW"])
            vault, code = select_vault_directory(
                directory_arg=None,
                has_flags=False,
                current_dir="/ws",
                resolve_workspace_context_fn=lambda _cwd: ("/ws", False),
                vault_manager_factory=lambda _root: manager,
                create_new_vault_fn=lambda _root: "/ws/NewVault",
            )
            self._assert(vault == "/ws/NewVault", "Debe devolver vault recién creado")
            self._assert(code is None, "No debe salir temprano tras crear vault")
            self._assert(manager.refresh_called is True, "Debe refrescar vaults tras creación")

            print("✅ Test: create_new exitoso refresca y retorna vault")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test global_selector_create_new_success falló: {e}")
            self.failed += 1

    def test_global_selector_create_new_cancel_then_pick_existing(self):
        try:
            manager = _FakeVaultManager("/ws", ["CREATE_NEW", "/ws/ExistingVault"])
            vault, code = select_vault_directory(
                directory_arg=None,
                has_flags=False,
                current_dir="/ws",
                resolve_workspace_context_fn=lambda _cwd: ("/ws", False),
                vault_manager_factory=lambda _root: manager,
                create_new_vault_fn=lambda _root: None,
            )
            self._assert(vault == "/ws/ExistingVault", "Debe permitir volver y seleccionar vault existente")
            self._assert(code is None, "No debe salir temprano")
            self._assert(manager.refresh_called is False, "No debe refrescar si creación se cancela")

            print("✅ Test: create_new cancelado permite seleccionar existente")
            self.passed += 1
        except Exception as e:
            print(f"❌ Test global_selector_create_new_cancel_then_pick_existing falló: {e}")
            self.failed += 1

    def run_all(self):
        print("\n🧪 TESTS: core/vault_selection.py")
        print("=" * 50)

        self.test_directory_arg_passthrough()
        self.test_flags_without_directory_use_dot()
        self.test_local_context_short_circuit()
        self.test_global_selector_exit()
        self.test_global_selector_create_new_success()
        self.test_global_selector_create_new_cancel_then_pick_existing()

        print(f"\n📊 Resultado: ✅ {self.passed} | ❌ {self.failed}")
        return self.failed == 0


if __name__ == "__main__":
    tester = TestCoreVaultSelection()
    success = tester.run_all()
    sys.exit(0 if success else 1)
