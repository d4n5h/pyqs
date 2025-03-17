PyQS
====

A Python port of the Node.js `qs <https://github.com/ljharb/qs>`_ library.

PyQS is a querystring parsing and stringifying library with some added security.

Installation
-----------

.. code-block:: bash

    pip install pyqs

Usage
-----

Parsing
~~~~~~~

.. code-block:: python

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

Stringifying
~~~~~~~~~~~

.. code-block:: python

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

Options
-------

For a complete list of options, please see the `GitHub repository <https://github.com/yourusername/pyqs#readme>`_.

License
-------

BSD-3-Clause, same as the original qs library. 