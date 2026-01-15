"""KMZ to GeoJSON Converter

Convert KMZ/KML files to GeoJSON with automatic attribute parsing.
"""

__version__ = '0.1.0'

from .converter import KMZConverter

__all__ = ['KMZConverter']


def get_gui_app():
    """Get the GUI application class (lazy import to avoid tkinter dependency)."""
    from .gui import KMZ2GeoJSONApp
    return KMZ2GeoJSONApp
