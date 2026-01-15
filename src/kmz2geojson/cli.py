"""Command-line interface for KMZ to GeoJSON converter."""

import json
import sys
from pathlib import Path

import click

from .converter import KMZConverter
from .exceptions import ConversionError


@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path), required=False)
@click.option('--compact', is_flag=True, help='Output compact JSON (no pretty printing)')
@click.option('--no-validate', is_flag=True, help='Skip GeoJSON validation')
@click.option('-v', '--verbose', is_flag=True, help='Verbose output')
@click.version_option(version='0.1.0')
def main(input_file, output_file, compact, no_validate, verbose):
    """
    Convert KMZ/KML files to GeoJSON format.

    Automatically parses HTML table attributes from descriptions.

    Examples:

        \b
        # Convert to file
        kmz2geojson input.kmz output.geojson

        \b
        # Output to stdout
        kmz2geojson input.kmz

        \b
        # Compact JSON
        kmz2geojson input.kmz output.geojson --compact

        \b
        # Verbose mode
        kmz2geojson input.kmz -v
    """
    try:
        converter = KMZConverter()

        if verbose:
            click.echo(f"Reading: {input_file}", err=True)

        # Convert
        geojson_data = converter.convert(
            input_path=input_file,
            output_path=output_file,
            pretty=not compact,
            validate=not no_validate
        )

        if verbose:
            feature_count = len(geojson_data.get('features', []))
            click.echo(f"Converted {feature_count} feature(s)", err=True)

        # If no output file, write to stdout
        if not output_file:
            indent = 2 if not compact else None
            output = json.dumps(geojson_data, indent=indent, ensure_ascii=False)
            click.echo(output)
        elif verbose:
            click.echo(f"Written to: {output_file}", err=True)

    except ConversionError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nAborted", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
