"""Custom exceptions for KMZ to GeoJSON conversion."""


class ConversionError(Exception):
    """Base exception for conversion errors."""
    pass


class KMZExtractionError(ConversionError):
    """Error extracting KML from KMZ."""
    pass


class KMLParseError(ConversionError):
    """Error parsing KML XML."""
    pass


class GeometryConversionError(ConversionError):
    """Error converting geometry."""
    pass


class ValidationError(ConversionError):
    """GeoJSON validation failed."""
    pass
