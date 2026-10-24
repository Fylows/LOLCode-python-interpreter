# VIBE CODED TREE PRINTING ALGORITHM #
def print_tree(node, prefix="", is_last=True, field_name=None):
    """Print an AST as a clean, centered tree."""
    if field_name is None:
        print(" AST ".center(60, "="))
        print(type(node).__name__)
    else:
        branch = "`-- " if is_last else "|-- "
        if hasattr(node, "__dataclass_fields__") or isinstance(node, list):
            print(prefix + branch + field_name)
        else:
            value = node.name if hasattr(node, "name") else repr(node)
            print(prefix + branch + f"{field_name}: {value}")
            return

    if isinstance(node, list):
        children = [(str(index), value) for index, value in enumerate(node)]
    elif hasattr(node, "__dataclass_fields__"):
        children = [
            (name, getattr(node, name))
            for name in node.__dataclass_fields__
            if getattr(node, name) is not None
        ]
    else:
        return

    child_prefix = prefix
    if field_name is not None:
        child_prefix += "    " if is_last else "|   "

    for index, (name, value) in enumerate(children):
        child_is_last = index == len(children) - 1
        if isinstance(value, list):
            print_tree(value, child_prefix, child_is_last, name)
        elif hasattr(value, "__dataclass_fields__"):
            print_tree(value, child_prefix, child_is_last, name)
        else:
            print_tree(value, child_prefix, child_is_last, name)
