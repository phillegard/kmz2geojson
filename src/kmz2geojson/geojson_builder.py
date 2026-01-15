"""Build GeoJSON FeatureCollection from parsed KML data."""

from typing import Dict, List, Optional
import geojson

from .kml_parser import Placemark
from .html_parser import HTMLTableParser
from .geometry import GeometryConverter
from .exceptions import ValidationError


class GeoJSONBuilder:
    """Build GeoJSON FeatureCollection from Placemarks."""

    def __init__(self):
        self.html_parser = HTMLTableParser()
        self.geom_converter = GeometryConverter()

    def build_feature_collection(
        self,
        placemarks: List[Placemark],
        validate: bool = True
    ) -> Dict:
        """
        Build GeoJSON FeatureCollection from Placemarks.

        Args:
            placemarks: List of Placemark objects
            validate: Whether to validate GeoJSON output

        Returns:
            GeoJSON FeatureCollection dict

        Raises:
            ValidationError: If validation fails
        """
        features = []

        for placemark in placemarks:
            feature = self._build_feature(placemark)
            if feature:
                features.append(feature)

        feature_collection = {
            'type': 'FeatureCollection',
            'features': features
        }

        if validate:
            self.validate(feature_collection)

        return feature_collection

    def _build_feature(self, placemark: Placemark) -> Optional[Dict]:
        """
        Build single GeoJSON Feature from Placemark.

        Args:
            placemark: Placemark object

        Returns:
            GeoJSON Feature dict or None if geometry conversion fails
        """
        # Parse attributes from HTML description
        html_attributes = self.html_parser.parse_attributes(placemark.description)

        # Parse attributes from ExtendedData
        extended_attributes = self.html_parser.parse_extended_data(placemark.extended_data)

        # Convert geometry
        geometry = self.geom_converter.convert(placemark.geometry_element)

        # Build properties: name, then HTML attrs, then ExtendedData (overwrites duplicates)
        properties = {'name': placemark.name}
        properties.update(html_attributes)
        properties.update(extended_attributes)

        # Build feature
        feature = {
            'type': 'Feature',
            'geometry': geometry,
            'properties': properties
        }

        return feature

    def validate(self, geojson_obj: Dict) -> bool:
        """
        Validate GeoJSON structure.

        Performs basic structural validation:
        - FeatureCollection has 'type' and 'features'
        - Features have 'type', 'geometry', 'properties'
        - Geometries have 'type' and 'coordinates' or 'geometries'

        Args:
            geojson_obj: GeoJSON object to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Basic structural validation
            if geojson_obj.get('type') != 'FeatureCollection':
                raise ValidationError("GeoJSON must be a FeatureCollection")

            features = geojson_obj.get('features')
            if not isinstance(features, list):
                raise ValidationError("FeatureCollection must have 'features' array")

            for i, feature in enumerate(features):
                if feature.get('type') != 'Feature':
                    raise ValidationError(f"Feature {i} must have type 'Feature'")

                if 'properties' not in feature:
                    raise ValidationError(f"Feature {i} must have 'properties'")

                # Geometry can be null
                geometry = feature.get('geometry')
                if geometry is not None:
                    self._validate_geometry(geometry, f"Feature {i}")

            return True

        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Validation error: {e}")

    def _validate_geometry(self, geometry: Dict, context: str):
        """Validate geometry structure."""
        if not isinstance(geometry, dict):
            raise ValidationError(f"{context}: geometry must be an object")

        geom_type = geometry.get('type')
        if not geom_type:
            raise ValidationError(f"{context}: geometry must have 'type'")

        # GeometryCollection has 'geometries', others have 'coordinates'
        if geom_type == 'GeometryCollection':
            if 'geometries' not in geometry:
                raise ValidationError(f"{context}: GeometryCollection must have 'geometries'")
            # Recursively validate each geometry
            for i, geom in enumerate(geometry.get('geometries', [])):
                self._validate_geometry(geom, f"{context}.geometries[{i}]")
        else:
            if 'coordinates' not in geometry:
                raise ValidationError(f"{context}: {geom_type} must have 'coordinates'")
