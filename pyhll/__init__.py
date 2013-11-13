"""Small library for in-memory cardinality computing."""

VERSION = (0, 1, 1)

__version__ = '.'.join(map(str, VERSION[0:3]))
__author__ = 'Lipin Dmitriy'
__contact__ = 'blackwithwhite666@gmail.com'
__homepage__ = 'https://github.com/blackwithwhite666/pyhll'
__docformat__ = 'restructuredtext'

# -eof meta-

from .hll import (
    Cardinality,
    precision_for_error,
    error_for_precision,
    bytes_for_precision,
    MIN_PRECISION,
    MAX_PRECISION,
)


