#!/usr/bin/env python3
"""CLI action dispatch helpers extracted from main entrypoint."""

import os
import re
from typing import Optional

from brackets.utils.content_parser import debug_content_parsing
from brackets.utils.file_finder import debug_files_in_directory
from brackets.utils.legacy_utils import test_emoji_pattern


def has_action_flags(args) -> bool:
    """Return True when any direct action flag is present in CLI args."""
    return any(
        [
            args.weekly,
            args.monthly,
            args.timer,
            args.consolidate,
            args.consolidate_year,
            args.list,
            args.debug,
            args.test_emoji,
            args.analyze,
        ]
    )


def dispatch_cli_action(args, manager, vault_directory: str) -> Optional[int]:
    """Execute direct CLI actions and return an exit code, or None for interactive mode."""
    if args.weekly:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            return 1
        print("🗓️ Creando bitácora semanal...")
        success = manager.weekly_gen.create_next_or_manual_weekly_bitacora()
        return 0 if success else 1

    if args.monthly:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            return 1
        print("📋 Creando archivo mensual...")
        success = manager.monthly_gen.create_next_monthly_topics()
        return 0 if success else 1

    if args.timer:
        from brackets.modules.pomodoro_timer import run_pomodoro_standalone

        run_pomodoro_standalone(vault_directory)
        return 0

    if args.consolidate:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            return 1
        print(f"📦 Consolidando mes {args.consolidate}...")
        match = re.match(r"(\d{4})-(\d{2})", args.consolidate)
        if not match:
            print("❌ Formato inválido. Use YYYY-MM (ejemplo: 2025-07)")
            return 1
        year = int(match.group(1))
        month = int(match.group(2))
        success = manager.month_consolidator.consolidate_month(year, month)
        return 0 if success else 1

    if args.consolidate_year:
        if not manager.bitacoras_enabled:
            print("❌ Bitácoras desactivadas por configuración (feature_flags.bitacoras_enabled=false)")
            return 1
        print(f"📅 Consolidando año {args.consolidate_year}...")
        try:
            year = int(args.consolidate_year)
            success = manager.year_consolidator.consolidate_year(year)
            return 0 if success else 1
        except ValueError:
            print("❌ Formato inválido. Use YYYY (ejemplo: 2025)")
            return 1

    if args.list:
        print("📊 Archivos recientes:")
        print("\n📝 Bitácoras semanales:")
        manager.weekly_gen.list_recent_weeks(10)
        print("\n📋 Archivos mensuales:")
        manager.monthly_gen.list_recent_months(5)
        return 0

    if args.debug:
        debug_files_in_directory(vault_directory)
        return 0

    if args.test_emoji:
        test_emoji_pattern()
        return 0

    if args.analyze:
        filepath = args.analyze
        if not os.path.exists(filepath):
            filepath = os.path.join(vault_directory, args.analyze)

        if os.path.exists(filepath):
            debug_content_parsing(filepath)
            return 0

        print(f"❌ Archivo no encontrado: {args.analyze}")
        return 1

    return None
