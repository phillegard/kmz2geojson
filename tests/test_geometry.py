"""Tests for geometry converter."""

import pytest
from lxml import etree

from kmz2geojson.geometry import GeometryConverter


class TestGeometryConverter:
    """Tests for GeometryConverter."""

    @pytest.fixture
    def converter(self):
        return GeometryConverter()

    def test_convert_none(self, converter):
        """Returns None for None input."""
        assert converter.convert(None) is None

    def test_convert_point(self, converter):
        """Converts Point geometry."""
        xml = """
        <Point>
            <coordinates>-122.0822035425683,37.42228990140251,0</coordinates>
        </Point>
        """
        elem = etree.fromstring(xml)
        result = converter.convert(elem)
        assert result == {
            "type": "Point",
            "coordinates": [-122.0822035425683, 37.42228990140251, 0.0]
        }

    def test_convert_linestring(self, converter):
        """Converts LineString geometry."""
        xml = """
        <LineString>
            <coordinates>-122.084,37.422,0 -122.085,37.423,0</coordinates>
        </LineString>
        """
        elem = etree.fromstring(xml)
        result = converter.convert(elem)
        assert result["type"] == "LineString"
        assert len(result["coordinates"]) == 2
        assert result["coordinates"][0] == [-122.084, 37.422, 0.0]

    def test_convert_polygon(self, converter):
        """Converts Polygon geometry."""
        xml = """
        <Polygon>
            <outerBoundaryIs>
                <LinearRing>
                    <coordinates>
                        -122.084,37.422,0
                        -122.085,37.422,0
                        -122.085,37.423,0
                        -122.084,37.423,0
                        -122.084,37.422,0
                    </coordinates>
                </LinearRing>
            </outerBoundaryIs>
        </Polygon>
        """
        elem = etree.fromstring(xml)
        result = converter.convert(elem)
        assert result["type"] == "Polygon"
        assert len(result["coordinates"]) == 1  # One ring (outer boundary)
        assert len(result["coordinates"][0]) == 5  # 5 points (closed ring)

    def test_convert_multigeometry_same_type(self, converter):
        """Converts MultiGeometry with same types to Multi* format."""
        xml = """
        <MultiGeometry>
            <Point><coordinates>-122.084,37.422,0</coordinates></Point>
            <Point><coordinates>-122.085,37.423,0</coordinates></Point>
        </MultiGeometry>
        """
        elem = etree.fromstring(xml)
        result = converter.convert(elem)
        assert result["type"] == "MultiPoint"
        assert len(result["coordinates"]) == 2

    def test_convert_multigeometry_mixed_types(self, converter):
        """Converts MultiGeometry with mixed types to GeometryCollection."""
        xml = """
        <MultiGeometry>
            <Point><coordinates>-122.084,37.422,0</coordinates></Point>
            <LineString><coordinates>-122.084,37.422,0 -122.085,37.423,0</coordinates></LineString>
        </MultiGeometry>
        """
        elem = etree.fromstring(xml)
        result = converter.convert(elem)
        assert result["type"] == "GeometryCollection"
        assert len(result["geometries"]) == 2

    def test_convert_unsupported_type(self, converter):
        """Returns None for unsupported geometry types."""
        xml = "<UnknownGeometry><coordinates>1,2,3</coordinates></UnknownGeometry>"
        elem = etree.fromstring(xml)
        assert converter.convert(elem) is None


class TestCoordinateParsing:
    """Tests for coordinate parsing."""

    @pytest.fixture
    def converter(self):
        return GeometryConverter()

    def test_parse_3d_coordinates(self, converter):
        """Parses coordinates with altitude."""
        coords = converter._parse_coordinates("-122.084,37.422,100")
        assert coords == [[-122.084, 37.422, 100.0]]

    def test_parse_2d_coordinates(self, converter):
        """Parses coordinates without altitude (defaults to 0)."""
        coords = converter._parse_coordinates("-122.084,37.422")
        assert coords == [[-122.084, 37.422, 0.0]]

    def test_parse_multiple_coordinates(self, converter):
        """Parses multiple coordinate tuples."""
        coords = converter._parse_coordinates("-122.084,37.422,0 -122.085,37.423,0")
        assert len(coords) == 2

    def test_parse_coordinates_with_whitespace(self, converter):
        """Handles extra whitespace in coordinates."""
        coords = converter._parse_coordinates("  -122.084,37.422,0   -122.085,37.423,0  ")
        assert len(coords) == 2

    def test_parse_empty_coordinates_raises(self, converter):
        """Raises error for empty coordinate string."""
        from kmz2geojson.exceptions import GeometryConversionError
        with pytest.raises(GeometryConversionError):
            converter._parse_coordinates("")
