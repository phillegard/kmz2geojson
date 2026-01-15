"""Parse HTML tables from KML descriptions to extract attributes."""

from typing import Any, Dict, Optional, Union
from bs4 import BeautifulSoup


class HTMLTableParser:
    """Extract attributes from HTML tables in KML descriptions."""

    def parse_attributes(self, html_description: Optional[str]) -> Dict[str, Any]:
        """
        Parse HTML table into key-value dictionary.

        Extracts attributes from HTML tables in the format:
        <tr><td>key</td><td>value</td></tr>

        Args:
            html_description: HTML string from KML description

        Returns:
            Dictionary of attributes {key: value}
            Returns empty dict if no table found or description is None
        """
        if not html_description:
            return {}

        try:
            soup = BeautifulSoup(html_description, 'html.parser')

            # Find all table rows
            rows = soup.find_all('tr')
            if not rows:
                return {}

            attributes = {}

            for row in rows:
                cells = row.find_all('td')

                # Skip rows that don't have exactly 2 cells (key-value pair)
                if len(cells) != 2:
                    continue

                # Extract key and value
                key = cells[0].get_text(strip=True)
                value_text = cells[1].get_text(strip=True)

                # Skip empty keys
                if not key:
                    continue

                # Coerce value to appropriate type
                value = self._coerce_type(value_text)

                attributes[key] = value

            return attributes

        except Exception:
            # If HTML parsing fails for any reason, return empty dict
            # This ensures graceful degradation
            return {}

    def _coerce_type(self, value: str) -> Union[str, int, float, None]:
        """
        Attempt to convert string to appropriate type.

        Rules:
        - "<Null>" or empty → None
        - Pure digits → int
        - Float pattern → float
        - Otherwise → string (stripped)

        Args:
            value: String value to coerce

        Returns:
            Coerced value
        """
        # Handle null/empty
        if not value or value == '<Null>':
            return None

        # Try int
        try:
            # Check if it looks like an int (no decimal point)
            if '.' not in value and value.lstrip('-').isdigit():
                return int(value)
        except ValueError:
            pass

        # Try float
        try:
            # Only convert to float if it has a decimal point
            if '.' in value:
                return float(value)
        except ValueError:
            pass

        # Return as string
        return value
