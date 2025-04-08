"""
Version management for CVR AAS Profile Manager.
"""

__version__ = "1.1.0"

def get_version():
    """Returns the current version of the application."""
    return __version__

def get_version_info():
    """Returns a tuple of version information (major, minor, patch)."""
    return tuple(map(int, __version__.split('.'))) 