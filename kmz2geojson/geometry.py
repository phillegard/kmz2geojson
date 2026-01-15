"""Convert KML geometry to GeoJSON geometry."""

from typing import Dict, List, Optional
from lxml import etree

from .exceptions import GeometryConversionError


class GeometryConverter:
    """Convert KML geometry elements to GeoJSON geometry."""

    NAMESPACES = {
        'kml': 'http://www.opengis.net/kml/2.2',
        'gx': 'http://www.google.com/kml/ext/2.2'
    }

    def convert(self, geometry_element: Optional[etree._Element]) -> Optional[Dict]:
        """
        Convert KML geometry element to GeoJSON geometry.

        Supported types:
        - Point
        - LineString
        - Polygon
        - MultiGeometry

        Args:
            geometry_element: KML geometry XML element

        Returns:
            GeoJSON geometry dict or None if conversion fails
        """
        if geometry_element is None:
            return None

        # Get tag name without namespace
        tag = geometry_element.tag
        if '}' in tag:
            tag = tag.split('}')[1]

        try:
            if tag == 'Point':
                return self._convert_point(geometry_element)
            elif tag == 'LineString':
                return self._convert_linestring(geometry_element)
            elif tag == 'Polygon':
                return self._convert_polygon(geometry_element)
            elif tag == 'MultiGeometry':
                return self._convert_multigeometry(geometry_element)
            elif tag == 'LinearRing':
                # LinearRing is like LineString
                return self._convert_linestring(geometry_element)
            else:
                # Unsupported geometry type
                return None

        except Exception as e:
            # If conversion fails, return None (graceful degradation)
            return None

    def _parse_coordinates(self, coord_text: str) -> List[List[float]]:
        """
        Parse KML coordinate string to GeoJSON format.

        KML format: "lon,lat,alt lon,lat,alt ..."
        GeoJSON format: [[lon, lat, alt], [lon, lat, alt], ...]

        Args:
            coord_text: KML coordinate string

        Returns:
            List of [lon, lat, alt] coordinate tuples

        Raises:
            GeometryConversionError: If coordinate parsing fails
        """
        if not coord_text:
            raise GeometryConversionError("Empty coordinate string")

        coordinates = []

        # Split by whitespace to get individual coordinate tuples
        coord_tuples = coord_text.strip().split()

        for coord_tuple in coord_tuples:
            if not coord_tuple:
                continue

            # Split by comma to get lon, lat, alt
            parts = coord_tuple.split(',')

            if len(parts) < 2:
                # Invalid coordinate format
                continue

            try:
                lon = float(parts[0])
                lat = float(parts[1])
                alt = float(parts[2]) if len(parts) >= 3 else 0.0

                coordinates.append([lon, lat, alt])
            except (ValueError, IndexError):
                # Skip invalid coordinates
                continue

        if not coordinates:
            raise GeometryConversionError("No valid coordinates found")

        return coordinates

    def _convert_point(self, element: etree._Element) -> Dict:
        """
        Convert Point to GeoJSON Point.

        Args:
            element: Point XML element

        Returns:
            GeoJSON Point geometry
        """
        coord_elem = element.find('kml:coordinates', namespaces=self.NAMESPACES)
        if coord_elem is None:
            coord_elem = element.find('coordinates')

        if coord_elem is None or not coord_elem.text:
            raise GeometryConversionError("Point has no coordinates")

        coordinates = self._parse_coordinates(coord_elem.text)

        if not coordinates:
            raise GeometryConversionError("Point has invalid coordinates")

        return {
            'type': 'Point',
            'coordinates': coordinates[0]  # Point uses single coordinate
        }

    def _convert_linestring(self, element: etree._Element) -> Dict:
        """
        Convert LineString to GeoJSON LineString.

        Args:
            element: LineString XML element

        Returns:
            GeoJSON LineString geometry
        """
        coord_elem = element.find('kml:coordinates', namespaces=self.NAMESPACES)
        if coord_elem is None:
            coord_elem = element.find('coordinates')

        if coord_elem is None or not coord_elem.text:
            raise GeometryConversionError("LineString has no coordinates")

        coordinates = self._parse_coordinates(coord_elem.text)

        return {
            'type': 'LineString',
            'coordinates': coordinates
        }

    def _convert_polygon(self, element: etree._Element) -> Dict:
        """
        Convert Polygon to GeoJSON Polygon.

        Handles outer boundary and inner boundaries (holes).

        Args:
            element: Polygon XML element

        Returns:
            GeoJSON Polygon geometry
        """
        # Find outer boundary
        outer_boundary = element.find('kml:outerBoundaryIs', namespaces=self.NAMESPACES)
        if outer_boundary is None:
            outer_boundary = element.find('outerBoundaryIs')

        if outer_boundary is None:
            raise GeometryConversionError("Polygon has no outer boundary")

        # Get LinearRing from outer boundary
        linear_ring = outer_boundary.find('kml:LinearRing', namespaces=self.NAMESPACES)
        if linear_ring is None:
            linear_ring = outer_boundary.find('LinearRing')

        if linear_ring is None:
            raise GeometryConversionError("Outer boundary has no LinearRing")

        # Get coordinates
        coord_elem = linear_ring.find('kml:coordinates', namespaces=self.NAMESPACES)
        if coord_elem is None:
            coord_elem = linear_ring.find('coordinates')

        if coord_elem is None or not coord_elem.text:
            raise GeometryConversionError("Polygon has no coordinates")

        outer_coords = self._parse_coordinates(coord_elem.text)
        all_coords = [outer_coords]

        # Find inner boundaries (holes)
        inner_boundaries = element.findall('kml:innerBoundaryIs', namespaces=self.NAMESPACES)
        if not inner_boundaries:
            inner_boundaries = element.findall('innerBoundaryIs')

        for inner_boundary in inner_boundaries:
            linear_ring = inner_boundary.find('kml:LinearRing', namespaces=self.NAMESPACES)
            if linear_ring is None:
                linear_ring = inner_boundary.find('LinearRing')

            if linear_ring is not None:
                coord_elem = linear_ring.find('kml:coordinates', namespaces=self.NAMESPACES)
                if coord_elem is None:
                    coord_elem = linear_ring.find('coordinates')

                if coord_elem is not None and coord_elem.text:
                    inner_coords = self._parse_coordinates(coord_elem.text)
                    all_coords.append(inner_coords)

        return {
            'type': 'Polygon',
            'coordinates': all_coords
        }

    def _convert_multigeometry(self, element: etree._Element) -> Dict:
        """
        Convert MultiGeometry to appropriate GeoJSON type.

        If all child geometries are the same type, converts to Multi* format
        (MultiPoint, MultiLineString, MultiPolygon). Otherwise, returns
        GeometryCollection.

        Args:
            element: MultiGeometry XML element

        Returns:
            GeoJSON Multi* geometry or GeometryCollection
        """
        geometries = []
        geometry_types = set()

        # Get all child elements
        for child in element:
            # Skip non-geometry children
            tag = child.tag
            if '}' in tag:
                tag = tag.split('}')[1]

            if tag in ['Point', 'LineString', 'Polygon', 'MultiGeometry', 'LinearRing']:
                geom = self.convert(child)
                if geom is not None:
                    geometries.append(geom)
                    geometry_types.add(geom['type'])

        if not geometries:
            raise GeometryConversionError("MultiGeometry has no valid geometries")

        # If all geometries are the same type, convert to Multi* format
        if len(geometry_types) == 1:
            geom_type = list(geometry_types)[0]

            if geom_type == 'LineString':
                return {
                    'type': 'MultiLineString',
                    'coordinates': [g['coordinates'] for g in geometries]
                }
            elif geom_type == 'Point':
                return {
                    'type': 'MultiPoint',
                    'coordinates': [g['coordinates'] for g in geometries]
                }
            elif geom_type == 'Polygon':
                return {
                    'type': 'MultiPolygon',
                    'coordinates': [g['coordinates'] for g in geometries]
                }

        # Mixed types or nested collections - use GeometryCollection
        return {
            'type': 'GeometryCollection',
            'geometries': geometries
        }
