# KMZ to GeoJSON Converter

Convert KMZ/KML files to GeoJSON with automatic attribute parsing from HTML tables.

## Features

- Converts KMZ and KML files to GeoJSON format
- Automatically parses attributes from HTML tables embedded in KML descriptions
- Handles varying attribute sets across different files
- Supports multiple geometry types (Point, LineString, Polygon, MultiGeometry)
- Type coercion: automatically converts numeric strings to int/float
- CLI tool with flexible output options
- Validates GeoJSON output

## Installation

```bash
# Install from source
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Convert to file
kmz2geojson input.kmz output.geojson

# Output to stdout (useful for piping)
kmz2geojson input.kmz

# Compact JSON (no pretty printing)
kmz2geojson input.kmz output.geojson --compact

# Verbose mode
kmz2geojson input.kmz output.geojson -v

# Skip validation
kmz2geojson input.kmz output.geojson --no-validate

# Show help
kmz2geojson --help

# Show version
kmz2geojson --version
```

### Python API

```python
from pathlib import Path
from kmz2geojson import KMZConverter

# Create converter
converter = KMZConverter()

# Convert to file
geojson_data = converter.convert(
    input_path=Path("input.kmz"),
    output_path=Path("output.geojson"),
    pretty=True,
    validate=True
)

# Convert without writing to file
geojson_data = converter.convert(
    input_path=Path("input.kmz")
)

# Access the data
for feature in geojson_data['features']:
    print(feature['properties']['name'])
    print(feature['geometry']['type'])
```

## How It Works

### The Problem

KML files often store feature attributes in HTML tables within the `<description>` field:

```xml
<description><![CDATA[
<table>
  <tr><td>FID</td><td>0</td></tr>
  <tr><td>STATE</td><td>Colorado</td></tr>
  <tr><td>START_STAT</td><td>16610.29203</td></tr>
</table>
]]></description>
```

These attributes are not accessible as proper properties when converted to GeoJSON using standard tools.

### The Solution

This tool automatically:

1. Extracts KML from KMZ archives (ZIP files)
2. Parses XML structure to find Placemarks
3. Detects HTML tables in descriptions
4. Extracts key-value pairs from table rows
5. Converts values to appropriate types (int, float, string, null)
6. Transforms KML geometry to GeoJSON format
7. Builds valid GeoJSON with all attributes as properties

## Example

```bash
kmz2geojson "input.kmz" output.geojson -v
```

Output:
```
Reading: input.kmz
Converted 1 feature(s)
Written to: output.geojson
```

The resulting GeoJSON contains:
- 1 feature (pipeline route)
- 94 attributes parsed from HTML table
- LineString geometry with 25 coordinate points
- All attributes properly typed (ints, floats, strings, nulls)

## Testing Your Output

1. **Visualize**: Paste your GeoJSON at [geojson.io](https://geojson.io)
2. **Validate**: Use [GeoJSONLint](https://geojsonlint.com/)
3. **Inspect**: Use `jq` to explore the data:
   ```bash
   kmz2geojson input.kmz | jq '.features[0].properties | keys'
   ```

## License

MIT License
