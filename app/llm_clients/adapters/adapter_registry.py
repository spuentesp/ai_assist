adapter_map = {}

# Do NOT import adapters here to avoid circular imports.


def register_adapter(name):
    def decorator(fn):
        if name not in adapter_map:
            adapter_map[name] = {}
        adapter_map[name][fn.__name__] = fn
        return fn
    return decorator
