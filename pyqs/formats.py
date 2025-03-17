"""
Formats module for PyQS.

Defines the formatting options for encoding and decoding query strings.
"""

class Format:
    """Format constants for query string encoding."""
    RFC1738 = 'RFC1738'
    RFC3986 = 'RFC3986'

# Default format to use
DEFAULT = Format.RFC3986

# Formatters for different encoding formats
formatters = {
    Format.RFC1738: lambda value: value.replace('%20', '+'),
    Format.RFC3986: lambda value: str(value)
}

# Export format constants
formats = {
    'default': DEFAULT,
    'formatters': formatters,
    'RFC1738': Format.RFC1738,
    'RFC3986': Format.RFC3986
} 