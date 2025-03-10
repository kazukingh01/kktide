import importlib.util


__all__ = [
    "load_module_from_file"
]


def load_module_from_file(file_path):
    spec = importlib.util.spec_from_file_location("config", file_path)
    loaded_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded_module)
    return loaded_module
