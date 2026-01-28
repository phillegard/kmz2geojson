"""Custom exceptions for KMZ to GeoJSON conversion."""


class ConversionError(Exception):
    """Base exception for conversion errors."""


class KMZExtractionError(ConversionError):
    """Error extracting KML from KMZ."""


class KMLParseError(ConversionError):
    """Error parsing KML XML."""


class GeometryConversionError(ConversionError):
    """Error converting geometry."""


class ValidationError(ConversionError):
    """GeoJSON validation failed."""
