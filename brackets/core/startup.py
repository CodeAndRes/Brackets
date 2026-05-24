#!/usr/bin/env python3
"""Startup orchestration for Brackets CLI."""

from typing import Callable, Optional

from brackets.core.cli_actions import dispatch_cli_action, has_action_flags
from brackets.core.vault_selection import select_vault_directory


def run_startup_flow(
    args,
    current_dir: str,
    manager_factory: Callable[[str], object],
    has_action_flags_fn: Callable[[object], bool] = has_action_flags,
    select_vault_directory_fn: Callable[..., tuple[Optional[str], Optional[int]]] = select_vault_directory,
    dispatch_cli_action_fn: Callable[[object, object, str], Optional[int]] = dispatch_cli_action,
) -> Optional[int]:
    """Run startup orchestration for CLI mode selection and command dispatch.

    Returns:
        Optional exit code. None means interactive flow ended naturally.
    """
    has_flags = has_action_flags_fn(args)
    vault_directory, early_exit_code = select_vault_directory_fn(
        directory_arg=args.directory,
        has_flags=has_flags,
        current_dir=current_dir,
    )

    if early_exit_code is not None:
        if early_exit_code == 0:
            print("\n👋 ¡Hasta luego!")
        return early_exit_code

    if vault_directory is None:
        vault_directory = "."

    manager = manager_factory(vault_directory)

    exit_code = dispatch_cli_action_fn(args, manager, vault_directory)
    if exit_code is not None:
        return exit_code

    manager.run()
    return None
