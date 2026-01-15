"""Main orchestrator for KMZ to GeoJSON conversion."""

import json
from pathlib import Path
from typing import Dict, Optional

from .kmz_extractor import KMZExtractor
from .kml_parser import KMLParser
from .geojson_builder import GeoJSONBuilder
from .exceptions import ConversionError


class KMZConverter:
    """Main orchestrator for KMZ to GeoJSON conversion."""

    def __init__(self):
        self.extractor = KMZExtractor()
        self.kml_parser = KMLParser()
        self.geojson_builder = GeoJSONBuilder()

    def convert(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        pretty: bool = True,
        validate: bool = True
    ) -> Dict:
        """
        Convert KMZ/KML to GeoJSON.

        Pipeline:
        1. Determine if input is KMZ or KML
        2. Extract/read KML content
        3. Parse KML to Placemarks
        4. Build GeoJSON
        5. Optionally validate
        6. Write to output or return

        Args:
            input_path: Path to KMZ or KML file
            output_path: Optional output path (if None, no file written)
            pretty: Whether to pretty-print JSON
            validate: Whether to validate GeoJSON

        Returns:
            GeoJSON dict

        Raises:
            ConversionError: If conversion fails
        """
        if not input_path.exists():
            raise ConversionError(f"Input file not found: {input_path}")

        # Step 1 & 2: Get KML content
        kml_content = self._get_kml_content(input_path)

        # Step 3: Parse KML to Placemarks
        placemarks = self.kml_parser.parse(kml_content)

        if not placemarks:
            raise ConversionError(
                f"No Placemarks found in {input_path}. "
                f"The file may be empty or not contain valid KML features."
            )

        # Step 4 & 5: Build and optionally validate GeoJSON
        geojson_data = self.geojson_builder.build_feature_collection(
            placemarks,
            validate=validate
        )

        # Step 6: Write to output if path provided
        if output_path:
            self._write_geojson(geojson_data, output_path, pretty)

        return geojson_data

    def _get_kml_content(self, input_path: Path) -> str:
        """
        Get KML content from KMZ or KML file.

        Args:
            input_path: Path to input file

        Returns:
            KML content as string

        Raises:
            ConversionError: If reading fails
        """
        # Check if file is KMZ (ZIP) or KML (XML)
        if self._is_kmz(input_path):
            # Extract from KMZ
            return self.extractor.extract_kml(input_path)
        else:
            # Read KML directly
            try:
                return input_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                raise ConversionError(
                    f"Failed to read {input_path} as UTF-8. "
                    f"Ensure the file is a valid KML file."
                )
            except Exception as e:
                raise ConversionError(f"Failed to read {input_path}: {e}")

    def _is_kmz(self, path: Path) -> bool:
        """
        Check if file is KMZ (ZIP) or KML (XML).

        Args:
            path: File path

        Returns:
            True if KMZ, False if KML
        """
        # Check by extension first
        if path.suffix.lower() == '.kmz':
            return True
        elif path.suffix.lower() == '.kml':
            return False

        # Check by file signature (magic bytes)
        try:
            with open(path, 'rb') as f:
                signature = f.read(4)
                # ZIP files start with PK\x03\x04 or PK\x05\x06
                return signature[:2] == b'PK'
        except Exception:
            # If we can't read the file, assume based on extension
            return path.suffix.lower() == '.kmz'

    def _write_geojson(self, geojson_data: Dict, output_path: Path, pretty: bool):
        """
        Write GeoJSON to file.

        Args:
            geojson_data: GeoJSON dict
            output_path: Output file path
            pretty: Whether to pretty-print

        Raises:
            ConversionError: If writing fails
        """
        try:
            # Create parent directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(geojson_data, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(geojson_data, f, ensure_ascii=False)

        except Exception as e:
            raise ConversionError(f"Failed to write output to {output_path}: {e}")
