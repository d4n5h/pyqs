"""
Utility functions for PyQS.

Contains helper functions for encoding, decoding, and manipulating query strings.
"""

import re
import urllib.parse
from typing import Any, Dict, List, Union, Callable, Optional, TypeVar

from .formats import formats

T = TypeVar('T')

# Create a hex table for URL encoding
HEX_TABLE = ['%' + (('0' + hex(i)[2:]) if i < 16 else hex(i)[2:]).upper() for i in range(256)]


def is_buffer(obj: Any) -> bool:
    """Check if an object is a buffer-like object."""
    return hasattr(obj, 'buffer') and callable(getattr(obj, 'buffer', None))


def is_regexp(obj: Any) -> bool:
    """Check if an object is a regular expression."""
    return isinstance(obj, type(re.compile('')))


def array_to_object(source: List[Any], options: Optional[Dict[str, Any]] = None) -> Dict[int, Any]:
    """Convert an array to an object with numeric keys."""
    options = options or {}
    obj = {}
    
    for i, item in enumerate(source):
        if item is not None:
            obj[i] = item
    
    return obj


def merge(target: Any, source: Any, options: Optional[Dict[str, Any]] = None) -> Any:
    """
    Merge two objects recursively.
    
    Similar to Object.assign() in JavaScript but handles nested objects and arrays.
    """
    options = options or {}
    
    if source is None:
        return target
    
    # If source is not a dict or list, handle it specially
    if not isinstance(source, dict) and not isinstance(source, list):
        if isinstance(target, list):
            target.append(source)
        elif isinstance(target, dict):
            if (options.get('plain_objects', False) or 
                options.get('allow_prototypes', False) or 
                source not in dir(dict())):
                target[source] = True
        else:
            return [target, source]
        
        return target
    
    # If target is not the same type as source, or is empty, handle specially
    if not target or not isinstance(target, type(source)):
        if isinstance(source, list):
            return source.copy()  # Return a copy of the source list
        elif isinstance(source, dict):
            return source.copy()  # Return a copy of the source dict
        else:
            return source
    
    # Handle merging lists
    if isinstance(target, list) and isinstance(source, list):
        # For lists, we append items from source to target
        result = target.copy()
        result.extend(source)
        return result
    
    # Handle merging dictionaries
    if isinstance(target, dict) and isinstance(source, dict):
        result = target.copy()
        
        # Merge each key from source into result
        for key, value in source.items():
            if key in result:
                # If both values are dicts or both are lists, merge recursively
                if (isinstance(result[key], dict) and isinstance(value, dict)) or \
                   (isinstance(result[key], list) and isinstance(value, list)):
                    result[key] = merge(result[key], value, options)
                else:
                    # Otherwise, just replace the value
                    result[key] = value
            else:
                # If key doesn't exist in result, just add it
                result[key] = value
        
        return result
    
    # If we get here, target and source are different types
    # In this case, we'll just return source
    return source


def assign(target: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Assign properties from source to target (shallow copy).
    
    Similar to Object.assign() in JavaScript.
    """
    for key, value in source.items():
        target[key] = value
    return target


def decode(string: str, decoder: Optional[Callable[[str], str]] = None, 
           charset: str = 'utf-8', kind: Optional[str] = None) -> str:
    """
    Decode a URL-encoded string.
    
    Args:
        string: The string to decode
        decoder: Optional custom decoder function
        charset: Character set to use (utf-8 or iso-8859-1)
        kind: Type of value being decoded ('key' or 'value')
    
    Returns:
        The decoded string
    """
    string_without_plus = string.replace('+', ' ')
    
    if charset == 'iso-8859-1':
        return urllib.parse.unquote(string_without_plus)
    
    # utf-8
    try:
        return urllib.parse.unquote(string_without_plus, encoding='utf-8')
    except Exception:
        return string_without_plus


def encode(string: Any, encoder: Optional[Callable[[str], str]] = None, 
           charset: str = 'utf-8', kind: Optional[str] = None, 
           format: Optional[str] = None) -> str:
    """
    Encode a string as a URL component.
    
    Args:
        string: The string to encode
        encoder: Optional custom encoder function
        charset: Character set to use (utf-8 or iso-8859-1)
        kind: Type of value being encoded ('key' or 'value')
        format: Format to use (RFC1738 or RFC3986)
    
    Returns:
        The URL-encoded string
    """
    if not string:
        return string
    
    # Convert to string if not already
    if isinstance(string, (bool, int, float)) or string is None:
        string = str(string)
    
    if charset == 'iso-8859-1':
        return urllib.parse.quote(string, safe='')
    
    # Process in chunks to avoid memory issues with very long strings
    limit = 1024
    result = []
    
    for i in range(0, len(string), limit):
        segment = string[i:i+limit]
        encoded_segment = []
        
        for char in segment:
            code_point = ord(char)
            
            # Characters that don't need encoding
            if (code_point == 0x2D or  # -
                code_point == 0x2E or  # .
                code_point == 0x5F or  # _
                code_point == 0x7E or  # ~
                (0x30 <= code_point <= 0x39) or  # 0-9
                (0x41 <= code_point <= 0x5A) or  # A-Z
                (0x61 <= code_point <= 0x7A) or  # a-z
                (format == formats['RFC1738'] and (code_point == 0x28 or code_point == 0x29))  # ( )
               ):
                encoded_segment.append(char)
                continue
            
            # ASCII characters
            if code_point < 0x80:
                encoded_segment.append(HEX_TABLE[code_point])
                continue
            
            # Two-byte UTF-8
            if code_point < 0x800:
                encoded_segment.append(
                    HEX_TABLE[0xC0 | (code_point >> 6)] +
                    HEX_TABLE[0x80 | (code_point & 0x3F)]
                )
                continue
            
            # Three-byte UTF-8 (excluding surrogates)
            if code_point < 0xD800 or code_point >= 0xE000:
                encoded_segment.append(
                    HEX_TABLE[0xE0 | (code_point >> 12)] +
                    HEX_TABLE[0x80 | ((code_point >> 6) & 0x3F)] +
                    HEX_TABLE[0x80 | (code_point & 0x3F)]
                )
                continue
            
            # Four-byte UTF-8 (surrogate pairs)
            # This is a simplification as Python strings are already Unicode
            # and don't use surrogate pairs internally like JavaScript
            encoded_segment.append(urllib.parse.quote(char))
        
        result.append(''.join(encoded_segment))
    
    return ''.join(result)


def compact(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove undefined and sparse values from an object.
    
    Args:
        obj: The object to compact
    
    Returns:
        A new object with undefined and sparse values removed
    """
    if not isinstance(obj, dict) and not isinstance(obj, list):
        return obj
    
    queue = [{'obj': {'o': obj}, 'prop': 'o'}]
    refs = []
    
    for i in range(len(queue)):
        item = queue[i]
        obj_value = item['obj'][item['prop']]
        
        if isinstance(obj_value, dict):
            for key, val in list(obj_value.items()):
                if val is None:
                    del obj_value[key]
                elif isinstance(val, (dict, list)) and val not in refs:
                    queue.append({'obj': obj_value, 'prop': key})
                    refs.append(val)
        
        elif isinstance(obj_value, list):
            # Remove None values and keep non-None values
            item['obj'][item['prop']] = [x for x in obj_value if x is not None]
            
            # Process nested objects in the list
            for j, val in enumerate(item['obj'][item['prop']]):
                if isinstance(val, (dict, list)) and val not in refs:
                    queue.append({'obj': item['obj'][item['prop']], 'prop': j})
                    refs.append(val)
    
    return obj


def combine(a: Any, b: Any) -> List[Any]:
    """Combine two values into a list."""
    if isinstance(a, list):
        if isinstance(b, list):
            return a + b
        else:
            return a + [b]
    else:
        if isinstance(b, list):
            return [a] + b
        else:
            return [a, b]


def maybe_map(val: Union[List[Any], Any], fn: Callable[[Any], Any]) -> Union[List[Any], Any]:
    """Apply a function to each item in a list or to a single value."""
    if isinstance(val, list):
        return [fn(item) for item in val]
    return fn(val) 