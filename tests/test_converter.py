"""Tests for main converter."""

import json
import pytest
from pathlib import Path

from kmz2geojson.converter import KMZConverter
from kmz2geojson.exceptions import ConversionError


class TestKMZConverter:
    """Tests for KMZConverter."""

    @pytest.fixture
    def converter(self):
        return KMZConverter()

    @pytest.fixture
    def sample_kml_file(self, tmp_path):
        """Creates a temporary KML file."""
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Document>
                <Placemark>
                    <name>Test Point</name>
                    <description><![CDATA[
                        <table>
                            <tr><td>Field1</td><td>Value1</td></tr>
                            <tr><td>Count</td><td>42</td></tr>
                        </table>
                    ]]></description>
                    <Point>
                        <coordinates>-122.084,37.422,0</coordinates>
                    </Point>
                </Placemark>
            </Document>
        </kml>
        """
        kml_file = tmp_path / "test.kml"
        kml_file.write_text(kml_content)
        return kml_file

    def test_convert_kml_file(self, converter, sample_kml_file):
        """Converts KML file to GeoJSON."""
        result = converter.convert(sample_kml_file)
        assert result["type"] == "FeatureCollection"
        assert len(result["features"]) == 1
        feature = result["features"][0]
        assert feature["properties"]["name"] == "Test Point"
        assert feature["properties"]["Field1"] == "Value1"
        assert feature["properties"]["Count"] == 42
        assert feature["geometry"]["type"] == "Point"

    def test_convert_writes_output_file(self, converter, sample_kml_file, tmp_path):
        """Writes output to file when path provided."""
        output_file = tmp_path / "output.geojson"
        converter.convert(sample_kml_file, output_path=output_file)
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        assert data["type"] == "FeatureCollection"

    def test_convert_compact_output(self, converter, sample_kml_file, tmp_path):
        """Writes compact JSON when pretty=False."""
        output_file = tmp_path / "output.geojson"
        converter.convert(sample_kml_file, output_path=output_file, pretty=False)
        content = output_file.read_text()
        # Compact JSON should not have newlines (except possibly at the end)
        assert "\n" not in content.strip()

    def test_convert_nonexistent_file_raises(self, converter, tmp_path):
        """Raises ConversionError for nonexistent file."""
        fake_path = tmp_path / "nonexistent.kml"
        with pytest.raises(ConversionError):
            converter.convert(fake_path)

    def test_convert_empty_kml_raises(self, converter, tmp_path):
        """Raises ConversionError for KML with no Placemarks."""
        kml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Document><name>Empty</name></Document>
        </kml>
        """
        kml_file = tmp_path / "empty.kml"
        kml_file.write_text(kml_content)
        with pytest.raises(ConversionError):
            converter.convert(kml_file)


class TestFileTypeDetection:
    """Tests for KMZ vs KML detection."""

    @pytest.fixture
    def converter(self):
        return KMZConverter()

    def test_detect_kml_by_extension(self, converter, tmp_path):
        """Detects KML by .kml extension."""
        kml_file = tmp_path / "test.kml"
        kml_file.write_text("<kml></kml>")
        assert converter._is_kmz(kml_file) is False

    def test_detect_kmz_by_extension(self, converter, tmp_path):
        """Detects KMZ by .kmz extension."""
        # Create a minimal ZIP file
        import zipfile
        kmz_file = tmp_path / "test.kmz"
        with zipfile.ZipFile(kmz_file, 'w') as zf:
            zf.writestr("doc.kml", "<kml></kml>")
        assert converter._is_kmz(kmz_file) is True

    def test_detect_kmz_by_magic_bytes(self, converter, tmp_path):
        """Detects KMZ by ZIP magic bytes."""
        import zipfile
        # Create ZIP with non-.kmz extension
        zip_file = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_file, 'w') as zf:
            zf.writestr("doc.kml", "<kml></kml>")
        assert converter._is_kmz(zip_file) is True
