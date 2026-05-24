import importlib
import sys
import os

class HotReloader:
    def __init__(self, watch_dir="aroxia"):
        self.watch_dir = watch_dir

    def reload_module(self, module_name):
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            return f"Reloaded {module_name}"
        else:
            return f"Module {module_name} not loaded."

    def apply_hotfix(self, file_path, new_content):
        with open(file_path, "w") as f:
            f.write(new_content)
        # Attempt to reload the module if it's part of the package
        if file_path.endswith(".py"):
            module_name = file_path.replace("/", ".").replace(".py", "")
            return self.reload_module(module_name)
        return "Hotfix applied to file."
