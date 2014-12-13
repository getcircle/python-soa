from importlib import import_module


# ported from django
# https://docs.djangoproject.com/en/dev/_modules/django/utils/module_loading/
def import_string(dotted_path):
    """Import a dotted module path.

    Return the attribute/class designated by the last name in the path. Raise
    ImportError if the import failed.

    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImportError(msg)

    module = import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            dotted_path,
            class_name,
        )
        raise ImportError(msg)
