"""Tests for GeoJSON builder."""

import pytest
from lxml import etree

from kmz2geojson.geojson_builder import GeoJSONBuilder
from kmz2geojson.kml_parser import Placemark
from kmz2geojson.exceptions import ValidationError


class TestGeoJSONBuilder:
    """Tests for GeoJSONBuilder."""

    @pytest.fixture
    def builder(self):
        return GeoJSONBuilder()

    @pytest.fixture
    def sample_geometry_element(self):
        """Creates a sample Point geometry element."""
        xml = "<Point><coordinates>-122.084,37.422,0</coordinates></Point>"
        return etree.fromstring(xml)

    def test_build_feature_collection_empty(self, builder):
        """Builds empty FeatureCollection from empty list."""
        result = builder.build_feature_collection([], validate=False)
        assert result["type"] == "FeatureCollection"
        assert result["features"] == []

    def test_build_feature_collection_single(self, builder, sample_geometry_element):
        """Builds FeatureCollection with single feature."""
        placemark = Placemark(
            name="Test",
            description=None,
            geometry_element=sample_geometry_element,
            style_url=None
        )
        result = builder.build_feature_collection([placemark])
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1
        assert result["features"][0]["properties"]["name"] == "Test"

    def test_build_feature_with_html_attributes(self, builder, sample_geometry_element):
        """Extracts attributes from HTML description."""
        html_desc = "<table><tr><td>Field1</td><td>Value1</td></tr></table>"
        placemark = Placemark(
            name="Test",
            description=html_desc,
            geometry_element=sample_geometry_element,
            style_url=None
        )
        result = builder.build_feature_collection([placemark])
        props = result["features"][0]["properties"]
        assert props["name"] == "Test"
        assert props["Field1"] == "Value1"

    def test_build_feature_with_extended_data(self, builder, sample_geometry_element):
        """Extracts attributes from ExtendedData."""
        ext_data_xml = """
        <ExtendedData>
            <Data name="ExtField"><value>ExtValue</value></Data>
        </ExtendedData>
        """
        ext_data = etree.fromstring(ext_data_xml)
        placemark = Placemark(
            name="Test",
            description=None,
            geometry_element=sample_geometry_element,
            style_url=None,
            extended_data=ext_data
        )
        result = builder.build_feature_collection([placemark])
        props = result["features"][0]["properties"]
        assert props["ExtField"] == "ExtValue"


class TestValidation:
    """Tests for GeoJSON validation."""

    @pytest.fixture
    def builder(self):
        return GeoJSONBuilder()

    def test_validate_valid_feature_collection(self, builder):
        """Validates correct FeatureCollection."""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0, 0]},
                    "properties": {"name": "Test"}
                }
            ]
        }
        assert builder.validate(geojson) is True

    def test_validate_invalid_type(self, builder):
        """Rejects non-FeatureCollection type."""
        with pytest.raises(ValidationError):
            builder.validate({"type": "Feature", "properties": {}})

    def test_validate_missing_features(self, builder):
        """Rejects missing features array."""
        with pytest.raises(ValidationError):
            builder.validate({"type": "FeatureCollection"})

    def test_validate_invalid_feature_type(self, builder):
        """Rejects feature with wrong type."""
        geojson = {
            "type": "FeatureCollection",
            "features": [{"type": "NotAFeature", "properties": {}}]
        }
        with pytest.raises(ValidationError):
            builder.validate(geojson)

    def test_validate_missing_geometry_coordinates(self, builder):
        """Rejects geometry missing coordinates."""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point"},
                    "properties": {}
                }
            ]
        }
        with pytest.raises(ValidationError):
            builder.validate(geojson)

    def test_validate_null_geometry(self, builder):
        """Allows null geometry."""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": None,
                    "properties": {"name": "No geometry"}
                }
            ]
        }
        assert builder.validate(geojson) is True

    def test_validate_geometry_collection(self, builder):
        """Validates GeometryCollection correctly."""
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "GeometryCollection",
                        "geometries": [
                            {"type": "Point", "coordinates": [0, 0]},
                            {"type": "LineString", "coordinates": [[0, 0], [1, 1]]}
                        ]
                    },
                    "properties": {}
                }
            ]
        }
        assert builder.validate(geojson) is True
