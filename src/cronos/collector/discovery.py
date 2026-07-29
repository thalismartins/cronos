from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from cronos.collector.interface import Collector
from cronos.collector.registry import registry


def discover_collectors() -> None:
    _load_builtin_collectors()
    _discover_entrypoint_collectors()


def _load_builtin_collectors() -> None:
    collectors_path = Path("collectors")
    if not collectors_path.exists():
        return

    for p in collectors_path.iterdir():
        if not p.is_dir() or not (p / "plugin.py").exists():
            continue
        module_name = f"collectors.{p.name}.plugin"
        try:
            mod = importlib.import_module(module_name)
            _register_from_module(mod)
        except ImportError:
            continue


def _discover_entrypoint_collectors() -> None:
    for entry_point in pkgutil.iter_modules():
        if entry_point.name.startswith("cronos_collector_"):
            try:
                mod = entry_point.module_finder.find_module(entry_point.name).load_module(entry_point.name)
                _register_from_module(mod)
            except ImportError:
                continue


def _register_from_module(module) -> None:
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, Collector) and attr is not Collector:
            instance = attr()
            registry[instance.id] = attr
