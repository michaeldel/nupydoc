import importlib
import os
import pkgutil

from typing import Optional


def is_standard_library(module: pkgutil.ModuleInfo) -> bool:  # TODO: find better heuristic
    return 'site-packages' not in module.module_finder.path

def walk_modules(path: Optional[str] = None, prefix: str = ""):
    for module in pkgutil.iter_modules([path] if path is not None else None):
        # ignore modules marked private by default
        if module.name.startswith('_'):
            continue
        if hasattr(module.module_finder, 'path') and is_standard_library(module):
            continue

        print(f"{prefix}{module.name}")

        if module.ispkg:
            subpath = os.path.join(module.module_finder.path, module.name)
            walk_modules(subpath, prefix=f"  {prefix}")

walk_modules()

