"""KMZ to GeoJSON Converter

Convert KMZ/KML files to GeoJSON with automatic attribute parsing.
"""

__version__ = '0.1.0'

from .converter import KMZConverter

__all__ = ['KMZConverter']
