# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python CLI tool that converts KMZ/KML files to GeoJSON format. The unique challenge it solves is parsing feature attributes from HTML tables embedded in KML `<description>` fields, which standard converters ignore.

## Development Commands

```bash
# Install in development mode
pip install -e .

# Run the CLI tool
kmz2geojson input.kmz output.geojson
kmz2geojson input.kmz output.geojson -v  # verbose mode
kmz2geojson input.kmz                    # output to stdout

# Test with sample file
kmz2geojson "820290 , 24 Yosemite to Foothills - CAM.kmz" output.geojson -v
```

## Architecture

### Conversion Pipeline

The conversion follows a linear pipeline orchestrated by `KMZConverter`:

```
KMZ/KML Input
    ↓
[KMZExtractor] → Extract doc.kml from ZIP (if KMZ)
    ↓
[KMLParser] → Parse XML to Placemark objects
    ↓
[GeoJSONBuilder] → For each Placemark:
    ├─ [HTMLTableParser] → Extract attributes from HTML table
    ├─ [GeometryConverter] → Convert KML geometry to GeoJSON
    └─ Build Feature with properties + geometry
    ↓
FeatureCollection Output
```

### Module Responsibilities

- **converter.py**: Main orchestrator, file I/O, format detection
- **kmz_extractor.py**: ZIP extraction (KMZ → KML)
- **kml_parser.py**: XML parsing with namespace handling, extracts Placemarks
- **html_parser.py**: Parses HTML tables from `<description>` → dict with type coercion
- **geometry.py**: KML coordinates → GeoJSON geometry (handles Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, GeometryCollection)
- **geojson_builder.py**: Assembles GeoJSON FeatureCollection, validates structure
- **cli.py**: Click-based CLI interface

### Key Data Structures

**Placemark** (kml_parser.py):
```python
@dataclass
class Placemark:
    name: str
    description: Optional[str]  # HTML content with table
    geometry_element: Optional[etree._Element]  # lxml element
    style_url: Optional[str]
```

### Critical Implementation Details

**HTML Table Parsing** (html_parser.py):
- Uses BeautifulSoup to handle potentially malformed HTML in CDATA sections
- Extracts `<tr><td>key</td><td>value</td></tr>` patterns
- Type coercion: "123" → int, "123.45" → float, "<Null>" → None, else string
- Graceful degradation: returns empty dict if no table found

**KML Namespace Handling** (kml_parser.py, geometry.py):
- KML uses namespaces: `http://www.opengis.net/kml/2.2`
- Both namespaced and non-namespaced parsing attempted for compatibility
- Use lxml's XPath with namespace dict for queries

**Coordinate Conversion** (geometry.py):
- KML format: `"lon,lat,alt lon,lat,alt"` (space-separated)
- GeoJSON format: `[[lon, lat, alt], [lon, lat, alt]]` (3D coordinates, altitude included)
- Altitude defaults to 0.0 if not present in KML
- All coordinates are 3D for consistency

**MultiGeometry Conversion** (geometry.py):
- KML's `<MultiGeometry>` intelligently converts based on child types
- If all children are same type → converts to Multi* format:
  - All LineStrings → `MultiLineString`
  - All Points → `MultiPoint`
  - All Polygons → `MultiPolygon`
- Mixed child types → `GeometryCollection`
- Recursive conversion for nested geometries

### Validation

The `geojson_builder.py` validator checks:
- FeatureCollection structure (type, features array)
- Feature structure (type, properties, geometry)
- Geometry structure (type, coordinates/geometries)
- GeometryCollection recursive validation

Does NOT use geojson library's `is_valid` (has issues with GeometryCollection).

## Testing the Tool

```bash
# Verify output structure
kmz2geojson input.kmz | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'Features: {len(data[\"features\"])}')
print(f'Attributes: {len(data[\"features\"][0][\"properties\"])}')
"

# Visualize output
kmz2geojson input.kmz > output.geojson
# Upload output.geojson to https://geojson.io

# Inspect with jq
kmz2geojson input.kmz | jq '.features[0].properties | keys'
```

## Common Extension Points

- **New geometry types**: Add handler in `geometry.py` `convert()` method
- **Different description formats**: Extend `html_parser.py` to handle non-table formats
- **Additional validation**: Extend `_validate_geometry()` in `geojson_builder.py`
- **Error handling**: Use custom exceptions from `exceptions.py`
