"""
Test script for PyQS.

This script demonstrates the basic usage of the PyQS library.
"""

from pyqs import parse, stringify

def test_parse():
    """Test parsing functionality."""
    print("Testing parse functionality:")
    
    # Basic parsing
    parsed = parse('foo=bar&baz=qux')
    print(f"Basic parsing: {parsed}")
    
    # Array parsing
    parsed = parse('foo[]=bar&foo[]=baz')
    print(f"Array parsing: {parsed}")
    
    # Nested object parsing
    parsed = parse('foo[bar]=baz&foo[qux]=quux')
    print(f"Nested object parsing: {parsed}")
    
    # Dot notation
    parsed = parse('foo.bar=baz', {'allow_dots': True})
    print(f"Dot notation parsing: {parsed}")
    
    # Comma-separated values
    parsed = parse('foo=bar,baz', {'comma': True})
    print(f"Comma-separated values: {parsed}")
    
    # Ignoring query prefix
    parsed = parse('?foo=bar&baz=qux', {'ignore_query_prefix': True})
    print(f"Ignoring query prefix: {parsed}")
    
    print()


def test_stringify():
    """Test stringifying functionality."""
    print("Testing stringify functionality:")
    
    # Basic stringifying
    query_string = stringify({'foo': 'bar', 'baz': 'qux'})
    print(f"Basic stringifying: {query_string}")
    
    # Array stringifying
    query_string = stringify({'foo': ['bar', 'baz']})
    print(f"Array stringifying: {query_string}")
    
    # Nested object stringifying
    query_string = stringify({'foo': {'bar': 'baz', 'qux': 'quux'}})
    print(f"Nested object stringifying: {query_string}")
    
    # Dot notation
    query_string = stringify({'foo': {'bar': 'baz'}}, {'allow_dots': True})
    print(f"Dot notation stringifying: {query_string}")
    
    # Array format: brackets
    query_string = stringify({'foo': ['bar', 'baz']}, {'array_format': 'brackets'})
    print(f"Array format (brackets): {query_string}")
    
    # Array format: repeat
    query_string = stringify({'foo': ['bar', 'baz']}, {'array_format': 'repeat'})
    print(f"Array format (repeat): {query_string}")
    
    # Array format: comma
    query_string = stringify({'foo': ['bar', 'baz']}, {'array_format': 'comma'})
    print(f"Array format (comma): {query_string}")
    
    # Add query prefix
    query_string = stringify({'foo': 'bar'}, {'add_query_prefix': True})
    print(f"Add query prefix: {query_string}")
    
    print()


def test_roundtrip():
    """Test round-trip functionality."""
    print("Testing round-trip functionality:")
    
    # Basic round-trip
    original = {'foo': 'bar', 'baz': 'qux'}
    query_string = stringify(original)
    parsed = parse(query_string)
    print(f"Original: {original}")
    print(f"Query string: {query_string}")
    print(f"Parsed: {parsed}")
    print(f"Round-trip successful: {original == parsed}")
    
    # Nested object round-trip
    original = {'foo': {'bar': 'baz', 'qux': 'quux'}}
    query_string = stringify(original)
    parsed = parse(query_string)
    print(f"Original: {original}")
    print(f"Query string: {query_string}")
    print(f"Parsed: {parsed}")
    print(f"Round-trip successful: {original == parsed}")
    
    # Array round-trip
    original = {'foo': ['bar', 'baz']}
    query_string = stringify(original)
    parsed = parse(query_string)
    print(f"Original: {original}")
    print(f"Query string: {query_string}")
    print(f"Parsed: {parsed}")
    print(f"Round-trip successful: {original == parsed}")
    
    print()


if __name__ == '__main__':
    test_parse()
    test_stringify()
    test_roundtrip() 