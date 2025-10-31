__all__ = ["__version__"]

# Version is dynamically determined from git tags via hatch-vcs
try:
    from ._version import __version__
except ImportError:
    # Fallback for development/editable installs
    try:
        from importlib.metadata import version, PackageNotFoundError
        __version__ = version("provenance-demo")
    except PackageNotFoundError:
        __version__ = "0.0.0.dev0"
