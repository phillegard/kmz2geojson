"""Tests for HTML table parser."""

import pytest
from lxml import etree

from kmz2geojson.html_parser import HTMLTableParser


class TestHTMLTableParser:
    """Tests for HTMLTableParser.parse_attributes()."""

    @pytest.fixture
    def parser(self):
        return HTMLTableParser()

    def test_parse_empty_description(self, parser):
        """Returns empty dict for None or empty description."""
        assert parser.parse_attributes(None) == {}
        assert parser.parse_attributes("") == {}

    def test_parse_td_td_format(self, parser):
        """Parses <td>key</td><td>value</td> format."""
        html = """
        <table>
            <tr><td>Name</td><td>Test Feature</td></tr>
            <tr><td>Count</td><td>42</td></tr>
        </table>
        """
        result = parser.parse_attributes(html)
        assert result == {"Name": "Test Feature", "Count": 42}

    def test_parse_th_td_format(self, parser):
        """Parses <th>key</th><td>value</td> format."""
        html = """
        <table>
            <tr><th>Name</th><td>Test Feature</td></tr>
            <tr><th>Value</th><td>123.45</td></tr>
        </table>
        """
        result = parser.parse_attributes(html)
        assert result == {"Name": "Test Feature", "Value": 123.45}

    def test_parse_no_table(self, parser):
        """Returns empty dict when no table found."""
        html = "<p>Just some text</p>"
        assert parser.parse_attributes(html) == {}

    def test_skip_empty_keys(self, parser):
        """Skips rows with empty keys."""
        html = """
        <table>
            <tr><td></td><td>value</td></tr>
            <tr><td>Name</td><td>Test</td></tr>
        </table>
        """
        result = parser.parse_attributes(html)
        assert result == {"Name": "Test"}

    def test_graceful_degradation_on_malformed_html(self, parser):
        """Returns empty dict on malformed HTML."""
        html = "<table><tr><td>unclosed"
        result = parser.parse_attributes(html)
        # Should not raise, may return partial or empty
        assert isinstance(result, dict)


class TestTypeCoercion:
    """Tests for HTMLTableParser._coerce_type()."""

    @pytest.fixture
    def parser(self):
        return HTMLTableParser()

    def test_coerce_integer(self, parser):
        """Converts integer strings to int."""
        assert parser._coerce_type("42") == 42
        assert parser._coerce_type("-10") == -10
        assert parser._coerce_type("0") == 0

    def test_coerce_float(self, parser):
        """Converts float strings to float."""
        assert parser._coerce_type("3.14") == 3.14
        assert parser._coerce_type("-2.5") == -2.5
        assert parser._coerce_type("0.0") == 0.0

    def test_coerce_null(self, parser):
        """Converts null markers to None."""
        assert parser._coerce_type("<Null>") is None
        assert parser._coerce_type("") is None

    def test_coerce_string(self, parser):
        """Keeps non-numeric strings as strings."""
        assert parser._coerce_type("hello") == "hello"
        assert parser._coerce_type("test 123") == "test 123"


class TestExtendedDataParser:
    """Tests for HTMLTableParser.parse_extended_data()."""

    @pytest.fixture
    def parser(self):
        return HTMLTableParser()

    def test_parse_none(self, parser):
        """Returns empty dict for None."""
        assert parser.parse_extended_data(None) == {}

    def test_parse_simple_data(self, parser):
        """Parses SimpleData elements."""
        xml = """
        <ExtendedData>
            <SchemaData>
                <SimpleData name="Field1">value1</SimpleData>
                <SimpleData name="Field2">42</SimpleData>
            </SchemaData>
        </ExtendedData>
        """
        elem = etree.fromstring(xml)
        result = parser.parse_extended_data(elem)
        assert result == {"Field1": "value1", "Field2": 42}

    def test_parse_data_with_value(self, parser):
        """Parses Data elements with value children."""
        xml = """
        <ExtendedData>
            <Data name="myField">
                <value>myValue</value>
            </Data>
        </ExtendedData>
        """
        elem = etree.fromstring(xml)
        result = parser.parse_extended_data(elem)
        assert result == {"myField": "myValue"}
