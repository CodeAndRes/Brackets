#!/usr/bin/env python3
"""Vault selection bootstrap helpers for CLI startup."""

import os
from typing import Callable, Optional, Tuple

from brackets.core.workspace_context import resolve_workspace_context


def select_vault_directory(
    directory_arg: Optional[str],
    has_flags: bool,
    current_dir: Optional[str] = None,
    resolve_workspace_context_fn: Callable[[str], Tuple[str, bool]] = resolve_workspace_context,
    vault_manager_factory: Optional[Callable[[str], object]] = None,
    create_new_vault_fn: Optional[Callable[[str], Optional[str]]] = None,
) -> tuple[Optional[str], Optional[int]]:
    """Resolve vault directory before BitacoraManager initialization.

    Returns:
        tuple(vault_directory, early_exit_code)
        - vault_directory: selected/derived vault path (or None if exiting).
        - early_exit_code: exit code when startup should end early.
    """
    if directory_arg is not None:
        return directory_arg, None

    if has_flags:
        scope_root, local_only = resolve_workspace_context_fn(current_dir or os.getcwd())
        if local_only:
            return scope_root, None

        print("❌ Para usar flags de acción debes ejecutar dentro de un vault local o indicar --directory.")
        return None, 2

    scope_root, local_only = resolve_workspace_context_fn(current_dir or os.getcwd())
    if local_only:
        return scope_root, None

    if vault_manager_factory is None:
        from brackets.managers.vault_manager import VaultManager

        vault_manager_factory = VaultManager

    if create_new_vault_fn is None:
        from brackets.utils.vault_creator import create_new_vault

        create_new_vault_fn = create_new_vault

    vault_mgr = vault_manager_factory(scope_root)

    while True:
        selected = vault_mgr.show_vault_menu()

        if selected is None:
            return None, 0

        if selected == "CREATE_NEW":
            new_vault_path = create_new_vault_fn(scope_root)
            if new_vault_path:
                vault_mgr.refresh_vaults()
                return new_vault_path, None
            continue

        return selected, None
