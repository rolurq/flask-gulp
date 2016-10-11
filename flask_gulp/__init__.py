from collections import namedtuple


Task = namedtuple('Task', ['function', 'items', 'watched'])
File = namedtuple('File', ['filename', 'rel_name', 'content'])

from .static import Static
from .extensions import extension

__all__ = [
    'Static',
    'extension'
]

__version__ = '0.3.0'
