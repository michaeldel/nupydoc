from __future__ import annotations

import importlib
import inspect
import os
import pkgutil

import setuptools  # fix import order warning in distutils

from dataclasses import dataclass, field
from types import ModuleType as Module
from typing import Iterable, List, Optional


@dataclass
class ModuleTree:
    name: str
    submodules: List[ModuleTree] = field(default_factory=list)

    def __iter__(self) -> Iterable[ModuleTree]:
        yield from self.submodules


def walk_modules(tree: ModuleTree, callback: callable, *, parent: Optional[Module] = None):
    prefix = '.' if parent else ''
    package = parent.__name__ if parent else None
    module = importlib.import_module(f'{prefix}{tree.name}', package=package)

    callback(tree.name, module, parent)

    walk_classes(module, callback, module)
    walk_routines(module, callback, module)
    walk_data(module, callback, module)

    for submodule in tree.submodules:
        walk_modules(submodule, callback, parent=module)


def walk_classes(obj: object, callback: callable, module: Module):
    for name, cls in inspect.getmembers(obj, inspect.isclass):
        if name.startswith('_'):
            continue
        callback(name, cls, module)


def walk_routines(obj: object, callback: callable, module: Module):
    for name, cls in inspect.getmembers(obj, inspect.isroutine):
        if name.startswith('_'):
            continue
        callback(name, cls, module)


def walk_data(obj: object, callback: callable, module: Module):
    for name, cls in inspect.getmembers(obj, isdata):
        if name.startswith('_'):
            continue
        callback(name, cls, module)


def is_standard_library(module: pkgutil.ModuleInfo) -> bool:  # TODO: find better heuristic
    return 'site-packages' not in module.module_finder.path


def isdata(obj: object) -> bool:
    return not (
        inspect.ismodule(obj) or inspect.isclass(obj) or inspect.isroutine(obj) or
        inspect.isframe(obj) or inspect.istraceback(obj) or inspect.iscode(obj)
    )


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


def process(name: str, obj: object, module: Optional[Module] = None):
    # assert module is None or getattr(module, name) == obj, (name, obj, module)

    if isinstance(obj, Module):
        print('MOD', f"{obj.__name__}")
    elif inspect.isclass(obj):
        print('CLS', f"{module.__name__}.{name}")
    elif inspect.isroutine(obj):
        print('FUN', f"{module.__name__}.{name}")
    elif isdata(obj):
        print('DAT', f"{module.__name__}.{name}")
    else:
        raise NotImplementedError

for tree in compute_module_tree():
    walk_modules(tree, callback=process)

