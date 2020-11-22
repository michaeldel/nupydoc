from __future__ import annotations

import importlib
import os
import pkgutil

import setuptools  # fix import order warning in distutils

from dataclasses import dataclass, field
from typing import Iterable, List, Optional



@dataclass
class ModuleTree:
    name: str
    submodules: List[ModuleTree] = field(default_factory=list)

    def __iter__(self) -> Iterable[ModuleTree]:
        yield from self.submodules


def walk_modules(tree: ModuleTree, callback: callable, *, package: str = ''):
    prefix = '.' if package else ''
    module = importlib.import_module(f'{prefix}{tree.name}', package=package)
    callback(module)
    for submodule in tree.submodules:
        walk_modules(submodule, callback, package=module.__name__)


def is_standard_library(module: pkgutil.ModuleInfo) -> bool:  # TODO: find better heuristic
    return 'site-packages' not in module.module_finder.path


def compute_module_tree(path: Optional[str] = None) -> Iterable[ModuleTree]:
    for module in pkgutil.iter_modules([path] if path is not None else None):
        # ignore modules marked private by default
        if module.name.startswith('_'):
            continue
        if hasattr(module.module_finder, 'path') and is_standard_library(module):
            continue

        tree = ModuleTree(name=module.name)

        if module.ispkg:
            subpath = os.path.join(module.module_finder.path, module.name)
            tree.submodules.extend(compute_module_tree(subpath))

        yield tree


for tree in compute_module_tree():
    walk_modules(tree, callback=lambda m: print(m.__name__))

