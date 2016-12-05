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


# ported from scrapy:
# https://github.com/scrapy/scrapy/blob/master/scrapy/utils/console.py
def start_python_console(namespace=None, noipython=False, banner=''):
    """Start Python console binded to the given namespace. If IPython is
    available, an IPython console will be started instead, unless `noipython`
    is True. Also, tab completion will be used on Unix systems.
    """
    if namespace is None:
        namespace = {}

    try:
        # use IPython if available
        try:
            if noipython:
                raise ImportError()

            try:
                from IPython.terminal.embed import InteractiveShellEmbed
                from IPython.terminal.ipapp import load_default_config
            except ImportError:
                from IPython.frontend.terminal.embed import (
                    InteractiveShellEmbed
                )
                from IPython.frontend.terminal.ipapp import (
                    load_default_config
                )

            config = load_default_config()
            shell = InteractiveShellEmbed(
                banner1=banner, user_ns=namespace, config=config)
            shell()
        except ImportError:
            import code
            # readline module is only available on unix systems
            try:
                import readline
            except ImportError:
                pass
            else:
                import rlcompleter
                readline.parse_and_bind("tab:complete")
            code.interact(banner=banner, local=namespace)
    except SystemExit:
        # raised when using exit() in python code.interact
        pass
