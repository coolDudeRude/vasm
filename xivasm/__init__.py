from importlib.metadata import version, PackageNotFoundError
from . import exceptions
from . import parser
from . import source
from .m4_wrapper import M4
from .resolver import Resolver
from .linker import Linker

try:
    __version__ = version("xivasm")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"


__all__ = ["__version__", "M4", "parser", "source", "Resolver", "Linker", "exceptions"]
