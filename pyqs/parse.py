"""
Parse module for PyQS.

Implements functions for parsing URL query strings into Python objects.
"""

import re
from typing import Any, Dict, List, Union, Callable, Optional, TypeVar, cast

from . import utils

T = TypeVar('T')

# Default parsing options
defaults = {
    'allow_dots': False,
    'allow_empty_arrays': False,
    'allow_prototypes': False,
    'allow_sparse': False,
    'array_limit': 20,
    'charset': 'utf-8',
    'charset_sentinel': False,
    'comma': False,
    'decode_dot_in_keys': False,
    'decoder': utils.decode,
    'delimiter': '&',
    'depth': 5,
    'duplicates': 'combine',  # 'combine', 'first', or 'last'
    'ignore_query_prefix': False,
    'interpret_numeric_entities': False,
    'parameter_limit': 1000,
    'parse_arrays': True,
    'plain_objects': False,
    'strict_depth': False,
    'strict_null_handling': False,
    'throw_on_limit_exceeded': False
}


def interpret_numeric_entities(string: str) -> str:
    """
    Convert HTML numeric entities to their corresponding characters.
    
    Args:
        string: The string containing numeric entities
        
    Returns:
        The string with numeric entities replaced by their characters
    """
    def replace_entity(match):
        number = int(match.group(1))
        return chr(number)
    
    return re.sub(r'&#(\d+);', replace_entity, string)


def parse_array_value(val: str, options: Dict[str, Any], current_array_length: int) -> Union[str, List[str]]:
    """
    Parse a value that might be an array.
    
    Args:
        val: The value to parse
        options: Parsing options
        current_array_length: Current length of the array
        
    Returns:
        The parsed value, which might be a list if comma-separated
    """
    if val and isinstance(val, str) and options.get('comma', False) and ',' in val:
        return val.split(',')
    
    if (options.get('throw_on_limit_exceeded', False) and 
        current_array_length >= options.get('array_limit', defaults['array_limit'])):
        array_limit = options.get('array_limit', defaults['array_limit'])
        suffix = '' if array_limit == 1 else 's'
        raise ValueError(f"Array limit exceeded. Only {array_limit} element{suffix} allowed in an array.")
    
    return val


# ISO-8859-1 sentinel value (encodeURIComponent('&#10003;'))
ISO_SENTINEL = 'utf8=%26%2310003%3B'

# UTF-8 sentinel value (encodeURIComponent('✓'))
CHARSET_SENTINEL = 'utf8=%E2%9C%93'


def parse_values(string: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse a query string into an object.
    
    Args:
        string: The query string to parse
        options: Parsing options
        
    Returns:
        A dictionary of parsed values
    """
    obj: Dict[str, Any] = {}
    
    # Clean the string
    clean_str = string
    if options.get('ignore_query_prefix', False):
        clean_str = clean_str.lstrip('?')
    
    # Replace square brackets
    clean_str = clean_str.replace('%5B', '[').replace('%5D', ']')
    
    # Split into parts
    limit = float('inf') if options.get('parameter_limit', defaults['parameter_limit']) == float('inf') else options.get('parameter_limit', defaults['parameter_limit'])
    parts = clean_str.split(
        options.get('delimiter', defaults['delimiter']), int(limit) + (1 if options.get('throw_on_limit_exceeded', False) else 0)
    )
    
    if options.get('throw_on_limit_exceeded', False) and len(parts) > limit:
        suffix = '' if limit == 1 else 's'
        raise ValueError(f"Parameter limit exceeded. Only {limit} parameter{suffix} allowed.")
    
    # Check for charset sentinel
    skip_index = -1
    charset = options.get('charset', defaults['charset'])
    
    if options.get('charset_sentinel', False):
        for i, part in enumerate(parts):
            if part.startswith('utf8='):
                if part == CHARSET_SENTINEL:
                    charset = 'utf-8'
                elif part == ISO_SENTINEL:
                    charset = 'iso-8859-1'
                skip_index = i
                break
    
    # Process each part
    for i, part in enumerate(parts):
        if i == skip_index:
            continue
        
        # Find the key/value separator
        bracket_equals_pos = part.find(']=')
        pos = bracket_equals_pos + 1 if bracket_equals_pos != -1 else part.find('=')
        
        key = None
        val = None
        
        if pos == -1:
            # No '=' sign, so it's just a key
            key = options.get('decoder', defaults['decoder'])(
                part, defaults['decoder'], charset, 'key'
            )
            val = '' if not options.get('strict_null_handling', False) else None
        else:
            # Has a key and value
            key = options.get('decoder', defaults['decoder'])(
                part[:pos], defaults['decoder'], charset, 'key'
            )
            
            if key is not None:
                val_str = part[pos + 1:]
                
                # Handle array values
                if isinstance(obj.get(key), list):
                    current_length = len(obj[key])
                else:
                    current_length = 0
                
                parsed_val = parse_array_value(val_str, options, current_length)
                
                # Apply decoder to each value
                if isinstance(parsed_val, list):
                    val = [options.get('decoder', defaults['decoder'])(v, defaults['decoder'], charset, 'value') for v in parsed_val]
                else:
                    val = options.get('decoder', defaults['decoder'])(parsed_val, defaults['decoder'], charset, 'value')
        
        # Handle numeric entities
        if val and options.get('interpret_numeric_entities', False) and charset == 'iso-8859-1':
            val = interpret_numeric_entities(str(val))
        
        # Handle array notation
        if '[]=' in part:
            val = [val] if not isinstance(val, list) else val
        
        # Add to result object
        if key is not None:
            existing = key in obj
            
            if existing and options.get('duplicates', defaults['duplicates']) == 'combine':
                obj[key] = utils.combine(obj[key], val)
            elif not existing or options.get('duplicates', defaults['duplicates']) == 'last':
                obj[key] = val
    
    return obj


def parse_object(chain: List[str], val: Any, options: Dict[str, Any], values_parsed: bool) -> Any:
    """
    Parse an object path and set the value.
    
    Args:
        chain: The chain of keys
        val: The value to set
        options: Parsing options
        values_parsed: Whether the values have already been parsed
        
    Returns:
        The parsed object
    """
    # Get the current array length if applicable
    current_array_length = 0
    if chain and chain[-1] == '[]':
        parent_key = chain[0] if len(chain) == 2 else chain[-2]
        if isinstance(val, dict) and parent_key in val:
            current_array_length = len(val[parent_key]) if isinstance(val[parent_key], list) else 0
    
    # Parse the value if needed
    leaf = val if values_parsed else parse_array_value(val, options, current_array_length)
    
    # Build the object from the leaf up
    for i in range(len(chain) - 1, -1, -1):
        root = chain[i]
        obj = None
        
        if root == '[]' and options.get('parse_arrays', True):
            # Handle empty array case
            if options.get('allow_empty_arrays', False) and (leaf == '' or (options.get('strict_null_handling', False) and leaf is None)):
                obj = []
            else:
                # Create an array with the leaf value
                obj = []
                if leaf is not None:
                    if isinstance(leaf, list):
                        obj.extend(leaf)
                    else:
                        obj.append(leaf)
        else:
            # Handle object case
            obj = {}
            
            # Clean the root key
            clean_root = root[1:-1] if root.startswith('[') and root.endswith(']') else root
            
            # Handle dot decoding in keys
            if options.get('decode_dot_in_keys', False):
                clean_root = clean_root.replace('%2E', '.')
            
            # Check if the key is an array index
            try:
                index = int(clean_root)
                if (
                    root != clean_root and  # It was in brackets
                    str(index) == clean_root and  # It's a valid integer
                    index >= 0 and  # Non-negative
                    options.get('parse_arrays', True) and  # Arrays are allowed
                    index <= options.get('array_limit', defaults['array_limit'])  # Within limit
                ):
                    # Create an array with the leaf at the specified index
                    obj = [None] * (index + 1)
                    obj[index] = leaf
                    leaf = obj
                    continue
            except ValueError:
                pass
            
            # Regular object property
            if clean_root != '__proto__' or options.get('allow_prototypes', False):
                obj[clean_root] = leaf
        
        leaf = obj
    
    return leaf


def parse_keys(given_key: str, val: Any, options: Dict[str, Any], values_parsed: bool) -> Any:
    """
    Parse a key with potential dot notation or brackets.
    
    Args:
        given_key: The key to parse
        val: The value to set
        options: Parsing options
        values_parsed: Whether the values have already been parsed
        
    Returns:
        The parsed object
    """
    if not given_key:
        return None
    
    # Transform dot notation to bracket notation if allowed
    key = given_key
    if options.get('allow_dots', False):
        key = re.sub(r'\.([^.[]+)', r'[\1]', key)
    
    # Extract keys using regex
    keys = []
    parent = ''
    
    # Match the parent part (before any brackets)
    parent_match = re.match(r'^([^\[\]]*)', key)
    if parent_match:
        parent = parent_match.group(1)
    
    if parent:
        # Check for prototype properties
        if (not options.get('plain_objects', False) and 
            parent in dir(dict()) and 
            not options.get('allow_prototypes', False)):
            return None
        
        keys.append(parent)
    
    # Extract all bracket parts
    depth = options.get('depth', defaults['depth'])
    bracket_parts = re.findall(r'\[([^\[\]]*)\]', key)
    
    # Process bracket parts up to the depth limit
    i = 0
    while i < len(bracket_parts) and (depth == 0 or i < depth):
        part = bracket_parts[i]
        
        # Check for prototype properties
        if (not options.get('plain_objects', False) and 
            part in dir(dict()) and 
            not options.get('allow_prototypes', False)):
            return None
        
        # Empty brackets mean array
        if part == '':
            keys.append('[]')
        else:
            keys.append(part)
        
        i += 1
    
    # If there are remaining parts and strict depth is enabled, throw an error
    if i < len(bracket_parts) and options.get('strict_depth', False):
        raise ValueError(f"Input depth exceeded depth option of {depth} and strictDepth is true")
    
    # Add any remaining parts as a single segment
    if i < len(bracket_parts):
        remaining = '[' + ']['.join(bracket_parts[i:]) + ']'
        keys.append(remaining)
    
    return parse_object(keys, val, options, values_parsed)


def normalize_parse_options(opts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Normalize and validate parsing options.
    
    Args:
        opts: User-provided options
        
    Returns:
        Normalized options
    """
    if not opts:
        return defaults.copy()
    
    options = {}
    
    # Validate allow_empty_arrays
    if 'allow_empty_arrays' in opts and not isinstance(opts['allow_empty_arrays'], bool):
        raise TypeError('`allow_empty_arrays` option can only be `True` or `False`, when provided')
    
    # Validate decode_dot_in_keys
    if 'decode_dot_in_keys' in opts and not isinstance(opts['decode_dot_in_keys'], bool):
        raise TypeError('`decode_dot_in_keys` option can only be `True` or `False`, when provided')
    
    # Validate decoder
    if 'decoder' in opts and opts['decoder'] is not None and not callable(opts['decoder']):
        raise TypeError('Decoder has to be a function.')
    
    # Validate charset
    if 'charset' in opts and opts['charset'] not in ('utf-8', 'iso-8859-1'):
        raise TypeError('The charset option must be either utf-8, iso-8859-1, or undefined')
    
    # Validate throw_on_limit_exceeded
    if 'throw_on_limit_exceeded' in opts and not isinstance(opts['throw_on_limit_exceeded'], bool):
        raise TypeError('`throw_on_limit_exceeded` option must be a boolean')
    
    # Set charset
    charset = opts.get('charset', defaults['charset'])
    
    # Set duplicates handling
    duplicates = opts.get('duplicates', defaults['duplicates'])
    if duplicates not in ('combine', 'first', 'last'):
        raise TypeError('The duplicates option must be either combine, first, or last')
    
    # Set allow_dots
    allow_dots = opts.get('allow_dots', opts.get('decode_dot_in_keys', False) or defaults['allow_dots'])
    
    # Copy defaults and override with user options
    options = defaults.copy()
    for key, value in opts.items():
        if key in defaults:
            if key == 'depth' and (isinstance(value, (int, float)) or value is False):
                options[key] = float(value) if value is not False else 0
            else:
                options[key] = value
    
    # Override specific options
    options['allow_dots'] = bool(allow_dots)
    options['charset'] = charset
    options['duplicates'] = duplicates
    
    return options


def parse(string: str, opts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Parse a query string into an object.
    
    Args:
        string: The query string to parse
        opts: Parsing options
        
    Returns:
        A dictionary of parsed values
    """
    options = normalize_parse_options(opts)
    
    if not string or string is None:
        return {} if not options.get('plain_objects', False) else {}
    
    # Parse the string
    if isinstance(string, str):
        obj = parse_values(string, options)
    else:
        obj = string
    
    result = {} if options.get('plain_objects', False) else {}
    
    # Process each key
    for key in obj:
        new_obj = parse_keys(key, obj[key], options, isinstance(string, str))
        if new_obj is not None:
            result = utils.merge(result, new_obj, options)
    
    # Compact if not allowing sparse arrays
    if options.get('allow_sparse', False) is True:
        return result
    
    return utils.compact(result) 