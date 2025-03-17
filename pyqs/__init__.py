"""
PyQS - A Python port of the Node.js qs library.

A querystring parsing and stringifying library with some added security.
"""

from .parse import parse
from .stringify import stringify
from .formats import formats

__version__ = '0.1.0'

__all__ = ['parse', 'stringify', 'formats'] 