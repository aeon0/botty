from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __copyright__, __author__, __author_email__
from .__version__ import __license__

from .beautifultable import (  # noqa F401
    BeautifulTable,
    BTRowCollection,
    BTColumnCollection,
    BTRowHeader,
    BTColumnHeader,
    BTBorder,
    __all__,
)
from . import enums
from .enums import *  # noqa


__all__ = __all__ + [
    "__title__",
    "__description__",
    "__url__",
    "__version__",
    "__copyright__",
    "__author__",
    "__author_email__",
    "__license__",
]


# To avoid duplicating enums name, dynamically add them to BeautifulTable
# class and __all__
for token in dir(enums):
    if (
        token.startswith("WEP_")
        or token.startswith("ALIGN_")
        or token.startswith("SM_")
        or token.startswith("STYLE_")
    ):
        setattr(BeautifulTable, token, getattr(enums, token))
        __all__.append(token)
