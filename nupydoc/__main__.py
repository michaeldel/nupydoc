import importlib
import pkgutil


def is_standard_library(module: pkgutil.ModuleInfo) -> bool:  # TODO: find better heuristic
    return 'site-packages' not in module.module_finder.path

for module in pkgutil.iter_modules():
    # ignore modules marked private by default
    if module.name.startswith('_'):
        continue
    if hasattr(module.module_finder, 'path') and is_standard_library(module):
        continue

    print(module.name)

