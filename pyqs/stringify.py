"""
Stringify module for PyQS.

Implements functions for converting Python objects to URL query strings.
"""

import datetime
from typing import Any, Dict, List, Union, Callable, Optional, TypeVar, cast

from . import utils
from .formats import formats

T = TypeVar('T')

# Array prefix generators
array_prefix_generators = {
    'brackets': lambda prefix, key=None: prefix + '[]',
    'comma': 'comma',
    'indices': lambda prefix, key: prefix + '[' + str(key) + ']',
    'repeat': lambda prefix, key=None: prefix
}

# Default format
default_format = formats['default']

# Default options
defaults = {
    'add_query_prefix': False,
    'allow_dots': False,
    'allow_empty_arrays': False,
    'array_format': 'indices',
    'charset': 'utf-8',
    'charset_sentinel': False,
    'comma_round_trip': False,
    'delimiter': '&',
    'encode': True,
    'encode_dot_in_keys': False,
    'encoder': utils.encode,
    'encode_values_only': False,
    'filter': None,
    'format': default_format,
    'formatter': formats['formatters'][default_format],
    'indices': False,  # deprecated
    'serialize_date': lambda date: date.isoformat(),
    'skip_nulls': False,
    'sort': None,
    'strict_null_handling': False
}


def is_non_nullish_primitive(val: Any) -> bool:
    """
    Check if a value is a non-null primitive.
    
    Args:
        val: The value to check
        
    Returns:
        True if the value is a string, number, boolean, or symbol
    """
    return isinstance(val, (str, int, float, bool)) and val is not None


# Sentinel object for cycle detection
sentinel = object()


def stringify_value(
    obj: Any,
    prefix: str,
    generate_array_prefix: Union[str, Callable],
    comma_round_trip: bool,
    allow_empty_arrays: bool,
    strict_null_handling: bool,
    skip_nulls: bool,
    encode_dot_in_keys: bool,
    encoder: Optional[Callable],
    filter_func: Optional[Union[Callable, List]],
    sort: Optional[Callable],
    allow_dots: bool,
    serialize_date: Callable,
    format_str: str,
    formatter: Callable,
    encode_values_only: bool,
    charset: str,
    side_channel: Dict[int, bool]
) -> List[str]:
    """
    Stringify a value recursively.
    
    Args:
        obj: The object to stringify
        prefix: The key prefix
        generate_array_prefix: Function to generate array prefixes
        comma_round_trip: Whether to handle comma-separated values
        allow_empty_arrays: Whether to allow empty arrays
        strict_null_handling: How to handle null values
        skip_nulls: Whether to skip null values
        encode_dot_in_keys: Whether to encode dots in keys
        encoder: Function to encode values
        filter_func: Function or list to filter keys
        sort: Function to sort keys
        allow_dots: Whether to allow dot notation
        serialize_date: Function to serialize dates
        format_str: Format string
        formatter: Function to format values
        encode_values_only: Whether to encode only values
        charset: Character set
        side_channel: Side channel for cycle detection
        
    Returns:
        List of stringified key-value pairs
    """
    # Check for cycles using object id instead of the object itself
    obj_id = id(obj)
    if obj_id in side_channel:
        raise ValueError("Cyclic object value")
    
    # Apply filter
    if callable(filter_func):
        obj = filter_func(prefix, obj)
    elif isinstance(obj, datetime.datetime):
        obj = serialize_date(obj)
    elif generate_array_prefix == 'comma' and isinstance(obj, list):
        obj = [serialize_date(x) if isinstance(x, datetime.datetime) else x for x in obj]
    
    # Handle null values
    if obj is None:
        if strict_null_handling:
            if encoder and not encode_values_only:
                return [formatter(encoder(prefix, defaults['encoder'], charset, 'key', format_str))]
            return [formatter(prefix)]
        obj = ''
    
    # Handle primitives
    if is_non_nullish_primitive(obj) or utils.is_buffer(obj):
        if encoder:
            key_value = prefix if encode_values_only else encoder(prefix, defaults['encoder'], charset, 'key', format_str)
            return [formatter(key_value) + '=' + formatter(encoder(obj, defaults['encoder'], charset, 'value', format_str))]
        return [formatter(prefix) + '=' + formatter(str(obj))]
    
    values = []
    
    # Handle undefined
    if obj is None:
        return values
    
    # Handle arrays and objects
    obj_keys = []
    
    if generate_array_prefix == 'comma' and isinstance(obj, list):
        # Join array elements with commas
        if encode_values_only and encoder:
            obj = [encoder(x, defaults['encoder'], charset, 'value', format_str) if x is not None else x for x in obj]
        obj_keys = [{'value': ','.join(str(x) for x in obj) if obj else None}]
    elif isinstance(filter_func, list):
        obj_keys = filter_func
    else:
        # Get object keys
        if isinstance(obj, dict):
            keys = list(obj.keys())
        elif isinstance(obj, list):
            keys = list(range(len(obj)))
        else:
            # Try to get object attributes
            try:
                keys = [k for k in dir(obj) if not k.startswith('_') and not callable(getattr(obj, k))]
            except:
                keys = []
        
        # Sort keys if needed
        if sort:
            keys.sort(key=sort)
        else:
            keys.sort() if not isinstance(obj, list) else None
        
        obj_keys = keys
    
    # Handle dots in keys
    encoded_prefix = prefix.replace('.', '%2E') if encode_dot_in_keys else prefix
    
    # Handle special case for arrays with one element
    adjusted_prefix = encoded_prefix + '[]' if comma_round_trip and isinstance(obj, list) and len(obj) == 1 else encoded_prefix
    
    # Handle empty arrays
    if allow_empty_arrays and isinstance(obj, list) and len(obj) == 0:
        return [adjusted_prefix + '[]']
    
    # Add object to side channel for cycle detection
    side_channel[obj_id] = True
    
    # Process each key
    for key in obj_keys:
        value = None
        
        if isinstance(key, dict) and 'value' in key:
            value = key['value']
        elif isinstance(obj, dict):
            value = obj[key]
        elif isinstance(obj, list) and isinstance(key, int):
            value = obj[key] if key < len(obj) else None
        else:
            # Try to get attribute
            try:
                value = getattr(obj, key)
            except:
                value = None
        
        # Skip nulls if requested
        if skip_nulls and value is None:
            continue
        
        # Handle dots in keys
        encoded_key = str(key).replace('.', '%2E') if allow_dots and encode_dot_in_keys else str(key)
        
        # Generate key prefix
        if isinstance(obj, list):
            if callable(generate_array_prefix):
                key_prefix = generate_array_prefix(adjusted_prefix, encoded_key)
            elif generate_array_prefix == 'comma':
                key_prefix = adjusted_prefix
            else:
                key_prefix = adjusted_prefix
        else:
            key_prefix = adjusted_prefix + ('.' + encoded_key if allow_dots else '[' + encoded_key + ']')
        
        # Create a new side channel for the value
        value_side_channel = side_channel.copy()
        
        # Recursively stringify the value
        stringified = stringify_value(
            value,
            key_prefix,
            generate_array_prefix,
            comma_round_trip,
            allow_empty_arrays,
            strict_null_handling,
            skip_nulls,
            encode_dot_in_keys,
            None if generate_array_prefix == 'comma' and encode_values_only and isinstance(obj, list) else encoder,
            filter_func,
            sort,
            allow_dots,
            serialize_date,
            format_str,
            formatter,
            encode_values_only,
            charset,
            value_side_channel
        )
        
        # Add to values
        values.extend(stringified)
    
    # Remove object from side channel
    del side_channel[obj_id]
    
    return values


def normalize_stringify_options(opts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Normalize and validate stringify options.
    
    Args:
        opts: User-provided options
        
    Returns:
        Normalized options
    """
    if not opts:
        return defaults.copy()
    
    # Validate allow_empty_arrays
    if 'allow_empty_arrays' in opts and not isinstance(opts['allow_empty_arrays'], bool):
        raise TypeError('`allow_empty_arrays` option can only be `True` or `False`, when provided')
    
    # Validate encode_dot_in_keys
    if 'encode_dot_in_keys' in opts and not isinstance(opts['encode_dot_in_keys'], bool):
        raise TypeError('`encode_dot_in_keys` option can only be `True` or `False`, when provided')
    
    # Validate encoder
    if 'encoder' in opts and opts['encoder'] is not None and not callable(opts['encoder']):
        raise TypeError('Encoder has to be a function.')
    
    # Validate charset
    charset = opts.get('charset', defaults['charset'])
    if 'charset' in opts and charset not in ('utf-8', 'iso-8859-1'):
        raise TypeError('The charset option must be either utf-8, iso-8859-1, or undefined')
    
    # Validate format
    format_str = formats['default']
    if 'format' in opts:
        if opts['format'] not in formats['formatters']:
            raise TypeError('Unknown format option provided.')
        format_str = opts['format']
    
    formatter = formats['formatters'][format_str]
    
    # Validate filter
    filter_func = defaults['filter']
    if 'filter' in opts and (callable(opts['filter']) or isinstance(opts['filter'], list)):
        filter_func = opts['filter']
    
    # Validate array format
    array_format = None
    if 'array_format' in opts and opts['array_format'] in array_prefix_generators:
        array_format = opts['array_format']
    elif 'indices' in opts:
        array_format = 'indices' if opts['indices'] else 'repeat'
    else:
        array_format = defaults['array_format']
    
    # Validate comma_round_trip
    if 'comma_round_trip' in opts and not isinstance(opts['comma_round_trip'], bool):
        raise TypeError('`comma_round_trip` must be a boolean, or absent')
    
    # Set allow_dots
    allow_dots = opts.get('allow_dots', opts.get('encode_dot_in_keys', False) or defaults['allow_dots'])
    
    # Create normalized options
    options = defaults.copy()
    
    # Override with user options
    for key, value in opts.items():
        if key in defaults:
            options[key] = value
    
    # Set specific options
    options['allow_dots'] = bool(allow_dots)
    options['charset'] = charset
    options['array_format'] = array_format
    options['format'] = format_str
    options['formatter'] = formatter
    options['filter'] = filter_func
    options['sort'] = opts.get('sort', defaults['sort'])
    
    return options


def stringify(obj: Any, opts: Optional[Dict[str, Any]] = None) -> str:
    """
    Convert an object to a query string.
    
    Args:
        obj: The object to stringify
        opts: Stringify options
        
    Returns:
        The query string
    """
    options = normalize_stringify_options(opts)
    
    obj_keys = []
    filter_func = None
    
    # Apply filter
    if callable(options['filter']):
        filter_func = options['filter']
        obj = filter_func('', obj)
    elif isinstance(options['filter'], list):
        filter_func = options['filter']
        obj_keys = filter_func
    
    # Handle non-object values
    if not isinstance(obj, dict) and not isinstance(obj, list) and not hasattr(obj, '__dict__'):
        return ''
    
    # Get array prefix generator
    array_format = options['array_format']
    generate_array_prefix = array_prefix_generators[array_format]
    comma_round_trip = generate_array_prefix == 'comma' and options['comma_round_trip']
    
    # Get object keys if not already set
    if not obj_keys:
        if isinstance(obj, dict):
            obj_keys = list(obj.keys())
        elif isinstance(obj, list):
            obj_keys = list(range(len(obj)))
        else:
            # Try to get object attributes
            try:
                obj_keys = [k for k in dir(obj) if not k.startswith('_') and not callable(getattr(obj, k))]
            except:
                obj_keys = []
    
    # Sort keys if needed
    if options['sort']:
        obj_keys.sort(key=options['sort'])
    
    # Stringify each key-value pair
    side_channel = {}
    keys = []
    
    for key in obj_keys:
        value = None
        
        if isinstance(obj, dict):
            value = obj[key]
        elif isinstance(obj, list) and isinstance(key, int):
            value = obj[key] if key < len(obj) else None
        else:
            # Try to get attribute
            try:
                value = getattr(obj, key)
            except:
                value = None
        
        # Skip nulls if requested
        if options['skip_nulls'] and value is None:
            continue
        
        # Stringify the key-value pair
        stringified = stringify_value(
            value,
            str(key),
            generate_array_prefix,
            comma_round_trip,
            options['allow_empty_arrays'],
            options['strict_null_handling'],
            options['skip_nulls'],
            options['encode_dot_in_keys'],
            options['encoder'] if options['encode'] else None,
            options['filter'],
            options['sort'],
            options['allow_dots'],
            options['serialize_date'],
            options['format'],
            options['formatter'],
            options['encode_values_only'],
            options['charset'],
            side_channel
        )
        
        # Add to keys
        keys.extend(stringified)
    
    # Join keys with delimiter
    joined = options['delimiter'].join(keys)
    
    # Add query prefix if requested
    prefix = '?' if options['add_query_prefix'] else ''
    
    # Add charset sentinel if requested
    if options['charset_sentinel']:
        if options['charset'] == 'iso-8859-1':
            # encodeURIComponent('&#10003;')
            prefix += 'utf8=%26%2310003%3B&'
        else:
            # encodeURIComponent('✓')
            prefix += 'utf8=%E2%9C%93&'
    
    return prefix + joined if joined else '' 