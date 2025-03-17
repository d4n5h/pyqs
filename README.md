# PyQS

A Python port of the Node.js [qs](https://github.com/ljharb/qs) library.

PyQS is a querystring parsing and stringifying library with some added security.

## Installation

```bash
pip install pyqs
```

## Usage

### Parsing

```python
from pyqs import parse

# Parse a query string
parsed = parse('foo=bar&baz=qux')
# Result: {'foo': 'bar', 'baz': 'qux'}

# Parse with arrays
parsed = parse('foo[]=bar&foo[]=baz')
# Result: {'foo': ['bar', 'baz']}

# Parse with nested objects
parsed = parse('foo[bar]=baz&foo[qux]=quux')
# Result: {'foo': {'bar': 'baz', 'qux': 'quux'}}

# Parse with custom options
parsed = parse('foo.bar=baz', {'allow_dots': True})
# Result: {'foo': {'bar': 'baz'}}
```

### Stringifying

```python
from pyqs import stringify

# Stringify an object
query_string = stringify({'foo': 'bar', 'baz': 'qux'})
# Result: 'foo=bar&baz=qux'

# Stringify an object with arrays
query_string = stringify({'foo': ['bar', 'baz']})
# Result: 'foo%5B0%5D=bar&foo%5B1%5D=baz'

# Stringify with custom options
query_string = stringify({'foo': {'bar': 'baz'}}, {'allow_dots': True})
# Result: 'foo.bar=baz'
```

## Options

### Parsing Options

- `allow_dots`: When `True`, enables dot notation for parsing nested objects (e.g., `foo.bar=baz`). Default: `False`.
- `allow_empty_arrays`: When `True`, allows parsing empty arrays (e.g., `foo[]=`). Default: `False`.
- `allow_prototypes`: When `True`, allows parsing keys that would overwrite object prototype properties. Default: `False`.
- `allow_sparse`: When `True`, allows parsing sparse arrays (e.g., `foo[1]=bar`). Default: `False`.
- `array_limit`: Maximum index limit for parsing arrays. Default: `20`.
- `charset`: Character set to use for parsing. Can be `'utf-8'` or `'iso-8859-1'`. Default: `'utf-8'`.
- `charset_sentinel`: When `True`, detects the charset from the query string. Default: `False`.
- `comma`: When `True`, allows parsing comma-separated values as arrays. Default: `False`.
- `decode_dot_in_keys`: When `True`, decodes dots in keys (e.g., `foo%2Ebar=baz`). Default: `False`.
- `delimiter`: Character used to separate key-value pairs. Default: `'&'`.
- `depth`: Maximum depth for parsing nested objects. Default: `5`.
- `duplicates`: How to handle duplicate keys. Can be `'combine'`, `'first'`, or `'last'`. Default: `'combine'`.
- `ignore_query_prefix`: When `True`, ignores the leading `?` character in the query string. Default: `False`.
- `interpret_numeric_entities`: When `True`, interprets numeric HTML entities as their corresponding characters. Default: `False`.
- `parameter_limit`: Maximum number of parameters to parse. Default: `1000`.
- `parse_arrays`: When `True`, enables parsing arrays. Default: `True`.
- `plain_objects`: When `True`, uses plain objects for parsing. Default: `False`.
- `strict_depth`: When `True`, throws an error if the depth limit is exceeded. Default: `False`.
- `strict_null_handling`: When `True`, treats keys without values as having a `None` value. Default: `False`.
- `throw_on_limit_exceeded`: When `True`, throws an error if the array or parameter limit is exceeded. Default: `False`.

### Stringifying Options

- `add_query_prefix`: When `True`, prepends a `?` to the result. Default: `False`.
- `allow_dots`: When `True`, enables dot notation for stringifying nested objects. Default: `False`.
- `allow_empty_arrays`: When `True`, allows stringifying empty arrays. Default: `False`.
- `array_format`: Format to use for stringifying arrays. Can be `'indices'`, `'brackets'`, `'repeat'`, or `'comma'`. Default: `'indices'`.
- `charset`: Character set to use for stringifying. Can be `'utf-8'` or `'iso-8859-1'`. Default: `'utf-8'`.
- `charset_sentinel`: When `True`, adds a charset sentinel to the result. Default: `False`.
- `comma_round_trip`: When `True`, enables round-trip support for comma-separated arrays. Default: `False`.
- `delimiter`: Character used to separate key-value pairs. Default: `'&'`.
- `encode`: When `True`, encodes the result. Default: `True`.
- `encode_dot_in_keys`: When `True`, encodes dots in keys. Default: `False`.
- `encode_values_only`: When `True`, only encodes values. Default: `False`.
- `format`: Format to use for encoding. Can be `'RFC1738'` or `'RFC3986'`. Default: `'RFC3986'`.
- `skip_nulls`: When `True`, skips keys with `None` values. Default: `False`.
- `strict_null_handling`: When `True`, treats `None` values specially. Default: `False`.

## License

BSD-3-Clause, same as the original qs library. 