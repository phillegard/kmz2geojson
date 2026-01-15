"""Tests for KML parser."""

import pytest

from kmz2geojson.kml_parser import KMLParser, Placemark
from kmz2geojson.exceptions import KMLParseError


class TestKMLParser:
    """Tests for KMLParser."""

    @pytest.fixture
    def parser(self):
        return KMLParser()

    def test_parse_simple_placemark(self, parser):
        """Parses a simple Placemark."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Document>
                <Placemark>
                    <name>Test Point</name>
                    <Point>
                        <coordinates>-122.084,37.422,0</coordinates>
                    </Point>
                </Placemark>
            </Document>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert len(placemarks) == 1
        assert placemarks[0].name == "Test Point"
        assert placemarks[0].geometry_element is not None

    def test_parse_placemark_with_description(self, parser):
        """Parses Placemark with description."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Placemark>
                <name>Test</name>
                <description><![CDATA[<table><tr><td>Key</td><td>Value</td></tr></table>]]></description>
                <Point><coordinates>0,0,0</coordinates></Point>
            </Placemark>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert len(placemarks) == 1
        assert placemarks[0].description is not None
        assert "table" in placemarks[0].description

    def test_parse_multiple_placemarks(self, parser):
        """Parses multiple Placemarks."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Document>
                <Placemark><name>Point 1</name><Point><coordinates>0,0,0</coordinates></Point></Placemark>
                <Placemark><name>Point 2</name><Point><coordinates>1,1,0</coordinates></Point></Placemark>
                <Placemark><name>Point 3</name><Point><coordinates>2,2,0</coordinates></Point></Placemark>
            </Document>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert len(placemarks) == 3

    def test_parse_without_namespace(self, parser):
        """Parses KML without namespace declaration."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml>
            <Placemark>
                <name>No Namespace</name>
                <Point><coordinates>0,0,0</coordinates></Point>
            </Placemark>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert len(placemarks) == 1
        assert placemarks[0].name == "No Namespace"

    def test_parse_placemark_with_style_url(self, parser):
        """Parses Placemark with styleUrl."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Placemark>
                <name>Styled</name>
                <styleUrl>#myStyle</styleUrl>
                <Point><coordinates>0,0,0</coordinates></Point>
            </Placemark>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert placemarks[0].style_url == "#myStyle"

    def test_parse_unnamed_placemark(self, parser):
        """Assigns 'Unnamed' to Placemarks without name."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Placemark>
                <Point><coordinates>0,0,0</coordinates></Point>
            </Placemark>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert placemarks[0].name == "Unnamed"

    def test_parse_invalid_xml_raises(self, parser):
        """Raises KMLParseError for invalid XML."""
        with pytest.raises(KMLParseError):
            parser.parse("not valid xml <unclosed")

    def test_parse_empty_kml(self, parser):
        """Returns empty list for KML with no Placemarks."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Document>
                <name>Empty Document</name>
            </Document>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert placemarks == []

    def test_parse_extended_data(self, parser):
        """Parses Placemark with ExtendedData."""
        kml = """<?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
            <Placemark>
                <name>With ExtendedData</name>
                <ExtendedData>
                    <Data name="field1"><value>val1</value></Data>
                </ExtendedData>
                <Point><coordinates>0,0,0</coordinates></Point>
            </Placemark>
        </kml>
        """
        placemarks = parser.parse(kml)
        assert placemarks[0].extended_data is not None
