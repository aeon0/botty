"""This module provides BeautifulTable class

It is intended for printing Tabular data to terminals.

Example
-------
>>> from beautifultable import BeautifulTable
>>> table = BeautifulTable()
>>> table.columns.header = ['1st column', '2nd column']
>>> for i in range(5):
...    table.rows.apppend([i, i*i])
...
>>> print(table)
+------------+------------+
| 1st column | 2nd column |
+------------+------------+
|     0      |     0      |
+------------+------------+
|     1      |     1      |
+------------+------------+
|     2      |     4      |
+------------+------------+
|     3      |     9      |
+------------+------------+
|     4      |     16     |
+------------+------------+
"""
from __future__ import division, unicode_literals

import copy
import csv
import warnings

from . import enums

from .utils import (
    pre_process,
    termwidth,
    deprecated,
    deprecated_param,
    deprecation_message,
    ensure_type,
)
from .compat import basestring, Iterable, to_unicode
from .base import BTBaseList
from .helpers import (
    BTRowCollection,
    BTColumnCollection,
    BTRowHeader,
    BTColumnHeader,
)


__all__ = [
    "BeautifulTable",
    "BTRowCollection",
    "BTColumnCollection",
    "BTRowHeader",
    "BTColumnHeader",
    "BTBorder",
]


class BTBorder(object):
    """Class to control how each section of the table's border is rendered.

    To disable a behaviour, just set its corresponding attribute
    to an empty string

    Attributes
    ----------

    top : str
        Character used to draw the top border.

    left : str
        Character used to draw the left border.

    bottom : str
        Character used to draw the bottom border.

    right : str
        Character used to draw the right border.

    top_left : str
        Left most character of the top border.

    bottom_left : str
        Left most character of the bottom border.

    bottom_right : str
        Right most character of the bottom border.

    top_right : str
        Right most character of the top border.

    header_left : str
        Left most character of the header separator.

    header_right : str
        Right most character of the header separator.

    top_junction : str
        Junction character for top border.

    left_junction : str
        Junction character for left border.

    bottom_junction : str
        Junction character for bottom border.

    right_junction : str
        Junction character for right border.
    """

    def __init__(
        self,
        top,
        left,
        bottom,
        right,
        top_left,
        bottom_left,
        bottom_right,
        top_right,
        header_left,
        header_right,
        top_junction,
        left_junction,
        bottom_junction,
        right_junction,
    ):
        self.top = left
        self.left = right
        self.bottom = top
        self.right = bottom

        self.top_left = top_left
        self.bottom_left = bottom_left
        self.bottom_right = bottom_right
        self.top_right = top_right

        self.header_left = header_left
        self.header_right = header_right

        self.top_junction = top_junction
        self.left_junction = left_junction
        self.bottom_junction = bottom_junction
        self.right_junction = right_junction


def _make_getter(attr):
    return lambda self: getattr(self, attr)


def _make_setter(attr):
    return lambda self, value: setattr(
        self, attr, ensure_type(value, basestring)
    )


for prop, attr in [
    (x, "_{}".format(x))
    for x in (
        "top",
        "left",
        "bottom",
        "right",
        "top_left",
        "bottom_left",
        "bottom_right",
        "top_right",
        "header_left",
        "header_right",
        "top_junction",
        "left_junction",
        "bottom_junction",
        "right_junction",
    )
]:
    setattr(BTBorder, prop, property(_make_getter(attr), _make_setter(attr)))


class BTTableData(BTBaseList):
    def __init__(self, table, value=None):
        if value is None:
            value = []
        self._table = table
        self._value = value

    def _get_canonical_key(self, key):
        return self._table.rows._canonical_key(key)

    def _get_ideal_length(self):
        pass


class BeautifulTable(object):
    """Utility Class to print data in tabular format to terminal.

    Parameters
    ----------
    maxwidth: int, optional
        maximum width of the table in number of characters. this is ignored
        when manually setting the width of the columns. if this value is too
        low with respect to the number of columns and width of padding, the
        resulting table may override it(default 80).

    default_alignment : int, optional
        Default alignment for new columns(default beautifultable.ALIGN_CENTER).

    default_padding : int, optional
        Default width of the left and right padding for new columns(default 1).

    precision : int, optional
        All float values will have maximum number of digits after the decimal,
        capped by this value(Default 3).

    serialno : bool, optional
        If true, a column will be rendered with serial numbers(**DEPRECATED**).

    serialno_header: str, optional
        The header of the serial number column if rendered(**DEPRECATED**).

    detect_numerics : bool, optional
        Whether numeric strings should be automatically detected(Default True).

    sign : SignMode, optional
        Parameter to control how signs in numeric data are displayed.
        (default beautifultable.SM_MINUS).

    Attributes
    ----------
    precision : int
        All float values will have maximum number of digits after the decimal,
        capped by this value(Default 3).

    detect_numerics : bool
        Whether numeric strings should be automatically detected(Default True).
    """

    @deprecated_param("1.0.0", "1.2.0", "sign_mode", "sign")
    @deprecated_param("1.0.0", "1.2.0", "numeric_precision", "precision")
    @deprecated_param("1.0.0", "1.2.0", "max_width", "maxwidth")
    @deprecated_param("1.0.0", "1.2.0", "serialno")
    @deprecated_param("1.0.0", "1.2.0", "serialno_header")
    def __init__(
        self,
        maxwidth=80,
        default_alignment=enums.ALIGN_CENTER,
        default_padding=1,
        precision=3,
        serialno=False,
        serialno_header="SN",
        detect_numerics=True,
        sign=enums.SM_MINUS,
        **kwargs
    ):

        kwargs.setdefault("max_width", None)
        if kwargs["max_width"] is not None:
            maxwidth = kwargs["max_width"]

        kwargs.setdefault("numeric_precision", None)
        if kwargs["numeric_precision"] is not None:
            precision = kwargs["numeric_precision"]

        kwargs.setdefault("sign_mode", None)
        if kwargs["sign_mode"] is not None:
            sign = kwargs["sign_mode"]

        self.precision = precision
        self._serialno = serialno
        self._serialno_header = serialno_header
        self.detect_numerics = detect_numerics

        self._sign = sign
        self.maxwidth = maxwidth

        self._ncol = 0
        self._data = BTTableData(self)

        self.rows = BTRowCollection(self)
        self.columns = BTColumnCollection(
            self, default_alignment, default_padding
        )

        self._header_separator = ""
        self._header_junction = ""
        self._column_separator = ""
        self._row_separator = ""
        self.border = ""
        self.set_style(enums.STYLE_DEFAULT)

    def __copy__(self):
        obj = type(self)()
        obj.__dict__.update(
            {k: copy.copy(v) for k, v in self.__dict__.items()}
        )

        obj.rows._table = obj
        obj.rows.header._table = obj

        obj.columns._table = obj
        obj.columns.header._table = obj
        obj.columns.alignment._table = obj
        obj.columns.width._table = obj
        obj.columns.padding_left._table = obj
        obj.columns.padding_right._table = obj

        obj._data._table = obj
        for row in obj._data:
            row._table = obj

        return obj

    def __deepcopy__(self, memo):
        obj = type(self)()
        obj.__dict__.update(
            {k: copy.deepcopy(v, memo) for k, v in self.__dict__.items()}
        )

        obj.rows._table = obj
        obj.rows.header._table = obj

        obj.columns._table = obj
        obj.columns.header._table = obj
        obj.columns.alignment._table = obj
        obj.columns.width._table = obj
        obj.columns.padding_left._table = obj
        obj.columns.padding_right._table = obj

        obj._data._table = obj
        for row in obj._data:
            row._table = obj

        return obj

    def __setattr__(self, name, value):
        attrs = (
            "left_border_char",
            "right_border_char",
            "top_border_char",
            "bottom_border_char",
            "header_separator_char",
            "column_separator_char",
            "row_separator_char",
            "intersect_top_left",
            "intersect_top_mid",
            "intersect_top_right",
            "intersect_header_left",
            "intersect_header_mid",
            "intersect_header_right",
            "intersect_row_left",
            "intersect_row_mid",
            "intersect_row_right",
            "intersect_bottom_left",
            "intersect_bottom_mid",
            "intersect_bottom_right",
        )
        if to_unicode(name) in attrs:
            warnings.warn(
                deprecation_message(name, "1.0.0", "1.2.0", None),
                FutureWarning,
            )
            value = ensure_type(value, basestring, name)
        super(BeautifulTable, self).__setattr__(name, value)

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTRowCollection.__len__,
        details="Use len(BeautifulTable.rows)' instead.",
    )
    def __len__(self):  # pragma: no cover
        return len(self.rows)

    @deprecated(
        "1.0.0" "1.2.0",
        BTRowCollection.__iter__,
        details="Use iter(BeautifulTable.rows)' instead.",
    )
    def __iter__(self):  # pragma: no cover
        return iter(self.rows)

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnCollection.__contains__,
        details="Use ''value' in BeautifulTable.{columns|rows}' instead.",
    )
    def __contains__(self, key):  # pragma: no cover
        if isinstance(key, basestring):
            return key in self.columns
        elif isinstance(key, Iterable):
            return key in self.rows
        else:
            raise TypeError(
                ("'key' must be str or Iterable, " "not {}").format(
                    type(key).__name__
                )
            )

    def __repr__(self):
        return repr(self._data)

    def __str__(self):
        if len(self.rows) == 0 or len(self.columns) == 0:
            return ""

        string_ = []
        for line in self._get_string([], append=False):
            string_.append(line)

        return "\n".join(string_)

    # ************************Properties Begin Here************************
    @property
    def shape(self):
        """Read only attribute which returns the shape of the table."""
        return (len(self.rows), len(self.columns))

    @property
    def sign(self):
        """Attribute to control how signs are displayed for numerical data.

        It can be one of the following:

        ========================  =============================================
         Option                    Meaning
        ========================  =============================================
         beautifultable.SM_PLUS    A sign should be used for both +ve and -ve
                                   numbers.

         beautifultable.SM_MINUS   A sign should only be used for -ve numbers.

         beautifultable.SM_SPACE   A leading space should be used for +ve
                                   numbers and a minus sign for -ve numbers.
        ========================  =============================================
        """
        return self._sign

    @sign.setter
    def sign(self, value):
        if not isinstance(value, enums.SignMode):
            allowed = (
                "{}.{}".format(type(self).__name__, i.name)
                for i in enums.SignMode
            )
            error_msg = "allowed values for sign are: " + ", ".join(allowed)
            raise ValueError(error_msg)
        self._sign = value

    @property
    def border(self):
        """Characters used to draw the border of the table.

        You can set this directly to a character or use it's several attribute
        to control how each section of the table is rendered.
        It is an instance of :class:`~.BTBorder`
        """
        return self._border

    @border.setter
    def border(self, value):
        self._border = BTBorder(
            top=value,
            left=value,
            bottom=value,
            right=value,
            top_left=value,
            bottom_left=value,
            bottom_right=value,
            top_right=value,
            header_left=value,
            header_right=value,
            top_junction=value,
            left_junction=value,
            bottom_junction=value,
            right_junction=value,
        )

    @property
    def junction(self):
        """Character used to draw junctions in the row separator."""
        return self._junction

    @junction.setter
    def junction(self, value):
        self._junction = ensure_type(value, basestring)

    @property
    @deprecated("1.0.0", "1.2.0", BTRowCollection.header.fget)
    def serialno(self):  # pragma: no cover
        return self._serialno

    @serialno.setter
    @deprecated("1.0.0", "1.2.0", BTRowCollection.header.fget)
    def serialno(self, value):  # pragma: no cover
        self._serialno = value

    @property
    @deprecated("1.0.0", "1.2.0")
    def serialno_header(self):  # pragma: no cover
        return self._serialno_header

    @serialno_header.setter
    @deprecated("1.0.0", "1.2.0")
    def serialno_header(self, value):  # pragma: no cover
        self._serialno_header = value

    @property
    @deprecated("1.0.0", "1.2.0", sign.fget)
    def sign_mode(self):  # pragma: no cover
        return self.sign

    @sign_mode.setter
    @deprecated("1.0.0", "1.2.0", sign.fget)
    def sign_mode(self, value):  # pragma: no cover
        self.sign = value

    @property
    def maxwidth(self):
        """get/set the maximum width of the table.

        The width of the table is guaranteed to not exceed this value. If it
        is not possible to print a given table with the width provided, this
        value will automatically adjust.
        """
        offset = (len(self.columns) - 1) * termwidth(self.columns.separator)
        offset += termwidth(self.border.left)
        offset += termwidth(self.border.right)
        self._maxwidth = max(self._maxwidth, offset + len(self.columns))
        return self._maxwidth

    @maxwidth.setter
    def maxwidth(self, value):
        self._maxwidth = value

    @property
    @deprecated("1.0.0", "1.2.0", maxwidth.fget)
    def max_table_width(self):  # pragma: no cover
        return self.maxwidth

    @max_table_width.setter
    @deprecated("1.0.0", "1.2.0", maxwidth.fget)
    def max_table_width(self, value):  # pragma: no cover
        self.maxwidth = value

    @property
    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnCollection.__len__,
        details="Use 'len(self.columns)' instead.",
    )
    def column_count(self):  # pragma: no cover
        return len(self.columns)

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.width_exceed_policy.fget)
    def width_exceed_policy(self):  # pragma: no cover
        return self.columns.width_exceed_policy

    @width_exceed_policy.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.width_exceed_policy.fget)
    def width_exceed_policy(self, value):  # pragma: no cover
        self.columns.width_exceed_policy = value

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.default_alignment.fget)
    def default_alignment(self):  # pragma: no cover
        return self.columns.default_alignment

    @default_alignment.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.default_alignment.fget)
    def default_alignment(self, value):  # pragma: no cover
        self.columns.default_alignment = value

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.default_padding.fget)
    def default_padding(self):  # pragma: no cover
        return self.columns.default_padding

    @default_padding.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.default_padding.fget)
    def default_padding(self, value):  # pragma: no cover
        self.columns.default_padding = value

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.width.fget)
    def column_widths(self):  # pragma: no cover
        return self.columns.width

    @column_widths.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.width.fget)
    def column_widths(self, value):  # pragma: no cover
        self.columns.width = value

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.header.fget)
    def column_headers(self):  # pragma: no cover
        return self.columns.header

    @column_headers.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.header.fget)
    def column_headers(self, value):  # pragma: no cover
        self.columns.header = value

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.alignment.fget)
    def column_alignments(self):  # pragma: no cover
        return self.columns.alignment

    @column_alignments.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.alignment.fget)
    def column_alignments(self, value):  # pragma: no cover
        self.columns.alignment = value

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.padding_left.fget)
    def left_padding_widths(self):  # pragma: no cover
        return self.columns.padding_left

    @left_padding_widths.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.padding_left.fget)
    def left_padding_widths(self, value):  # pragma: no cover
        self.columns.padding_left = value

    @property
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.padding_right.fget)
    def right_padding_widths(self):  # pragma: no cover
        return self.columns.padding_right

    @right_padding_widths.setter
    @deprecated("1.0.0", "1.2.0", BTColumnCollection.padding_right.fget)
    def right_padding_widths(self, value):  # pragma: no cover
        self.columns.padding_right = value

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnCollection.__getitem__,
        details="Use 'BeautifulTable.{columns|rows}[key]' instead.",
    )
    def __getitem__(self, key):  # pragma: no cover
        if isinstance(key, basestring):
            return self.columns[key]
        return self.rows[key]

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnCollection.__setitem__,
        details="Use 'BeautifulTable.{columns|rows}[key]' instead.",
    )
    def __setitem__(self, key, value):  # pragma: no cover
        if isinstance(key, basestring):
            self.columns[key] = value
        else:
            self.rows[key] = value

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnCollection.__delitem__,
        details="Use 'BeautifulTable.{columns|rows}[key]' instead.",
    )
    def __delitem__(self, key):  # pragma: no cover
        if isinstance(key, basestring):
            del self.columns[key]
        else:
            del self.rows[key]

    # *************************Properties End Here*************************

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnCollection.__getitem__,
        details="Use 'BeautifulTable.columns[key]' instead.",
    )
    def get_column(self, key):  # pragma: no cover
        return self.columns[key]

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnHeader.__getitem__,
        details="Use 'BeautifulTable.columns.header[key]' instead.",
    )
    def get_column_header(self, index):  # pragma: no cover
        return self.columns.header[index]

    @deprecated(
        "1.0.0",
        "1.2.0",
        BTColumnHeader.__getitem__,
        details="Use 'BeautifulTable.columns.header.index(header)' instead.",
    )
    def get_column_index(self, header):  # pragma: no cover
        return self.columns.header.index(header)

    @deprecated("1.0.0", "1.2.0", BTRowCollection.filter)
    def filter(self, key):  # pragma: no cover
        return self.rows.filter(key)

    @deprecated("1.0.0", "1.2.0", BTRowCollection.sort)
    def sort(self, key, reverse=False):  # pragma: no cover
        self.rows.sort(key, reverse=reverse)

    @deprecated("1.0.0", "1.2.0", BTRowCollection.reverse)
    def reverse(self, value):  # pragma: no cover
        self.rows.reverse()

    @deprecated("1.0.0", "1.2.0", BTRowCollection.pop)
    def pop_row(self, index=-1):  # pragma: no cover
        return self.rows.pop(index)

    @deprecated("1.0.0", "1.2.0", BTRowCollection.insert)
    def insert_row(self, index, row):  # pragma: no cover
        return self.rows.insert(index, row)

    @deprecated("1.0.0", "1.2.0", BTRowCollection.append)
    def append_row(self, value):  # pragma: no cover
        self.rows.append(value)

    @deprecated("1.0.0", "1.2.0", BTRowCollection.update)
    def update_row(self, key, value):  # pragma: no cover
        self.rows.update(key, value)

    @deprecated("1.0.0", "1.2.0", BTColumnCollection.pop)
    def pop_column(self, index=-1):  # pragma: no cover
        return self.columns.pop(index)

    @deprecated("1.0.0", "1.2.0", BTColumnCollection.insert)
    def insert_column(self, index, header, column):  # pragma: no cover
        self.columns.insert(index, column, header)

    @deprecated("1.0.0", "1.2.0", BTColumnCollection.append)
    def append_column(self, header, column):  # pragma: no cover
        self.columns.append(column, header)

    @deprecated("1.0.0", "1.2.0", BTColumnCollection.update)
    def update_column(self, header, column):  # pragma: no cover
        self.columns.update(header, column)

    def set_style(self, style):
        """Set the style of the table from a predefined set of styles.

        Parameters
        ----------
        style: Style

            It can be one of the following:

            * beautifultable.STYLE_DEFAULT
            * beautifultable.STYLE_NONE
            * beautifultable.STYLE_DOTTED
            * beautifultable.STYLE_MYSQL
            * beautifultable.STYLE_SEPARATED
            * beautifultable.STYLE_COMPACT
            * beautifultable.STYLE_MARKDOWN
            * beautifultable.STYLE_RESTRUCTURED_TEXT
            * beautifultable.STYLE_BOX
            * beautifultable.STYLE_BOX_DOUBLED
            * beautifultable.STYLE_BOX_ROUNDED
            * beautifultable.STYLE_GRID
        """
        if not isinstance(style, enums.Style):
            allowed = (
                "{}.{}".format(type(self).__name__, i.name)
                for i in enums.Style
            )
            error_msg = "allowed values for style are: " + ", ".join(allowed)
            raise ValueError(error_msg)
        style_template = style.value
        self.border.left = style_template.left_border_char
        self.border.right = style_template.right_border_char
        self.border.top = style_template.top_border_char
        self.border.bottom = style_template.bottom_border_char

        self.border.top_left = style_template.intersect_top_left
        self.border.bottom_left = style_template.intersect_bottom_left
        self.border.bottom_right = style_template.intersect_bottom_right
        self.border.top_right = style_template.intersect_top_right

        self.border.header_left = style_template.intersect_header_left
        self.border.header_right = style_template.intersect_header_right

        self.columns.header.separator = style_template.header_separator_char
        self.columns.separator = style_template.column_separator_char
        self.rows.separator = style_template.row_separator_char

        self.border.top_junction = style_template.intersect_top_mid
        self.border.left_junction = style_template.intersect_row_left
        self.border.bottom_junction = style_template.intersect_bottom_mid
        self.border.right_junction = style_template.intersect_row_right
        self.columns.header.junction = style_template.intersect_header_mid
        self.junction = style_template.intersect_row_mid

    def _compute_width(self):
        """Calculate width of column automatically based on data."""
        table_width = self._width
        lpw, rpw = self.columns.padding_left, self.columns.padding_right
        pad_widths = [(lpw[i] + rpw[i]) for i in range(len(self.columns))]
        maxwidths = [0 for index in range(len(self.columns))]
        offset = table_width - sum(self.columns.width) + sum(pad_widths)
        self._maxwidth = max(self._maxwidth, offset + len(self.columns))

        for index, header in enumerate(self.columns.header):
            max_length = 0
            for i in pre_process(
                header, self.detect_numerics, self.precision, self.sign.value
            ).split("\n"):
                output_str = pre_process(
                    i,
                    self.detect_numerics,
                    self.precision,
                    self.sign.value,
                )
                max_length = max(max_length, termwidth(output_str))
            maxwidths[index] += max_length

        for index, column in enumerate(zip(*self._data)):
            max_length = maxwidths[index]
            for i in column:
                for j in pre_process(
                    i, self.detect_numerics, self.precision, self.sign.value
                ).split("\n"):
                    output_str = pre_process(
                        j,
                        self.detect_numerics,
                        self.precision,
                        self.sign.value,
                    )
                    max_length = max(max_length, termwidth(output_str))
            maxwidths[index] = max_length

        sum_ = sum(maxwidths)
        desired_sum = self._maxwidth - offset

        # Set flag for columns who are within their fair share
        temp_sum = 0
        flag = [0] * len(maxwidths)
        for i, width in enumerate(maxwidths):
            if width <= int(desired_sum / len(self.columns)):
                temp_sum += width
                flag[i] = 1
            else:
                # Allocate atleast 1 character width to the column
                temp_sum += 1

        avail_space = desired_sum - temp_sum
        actual_space = sum_ - temp_sum
        shrinked_columns = {}

        # Columns which exceed their fair share should be shrinked based on
        # how much space is left for the table
        for i, width in enumerate(maxwidths):
            self.columns.width[i] = width
            if not flag[i]:
                new_width = 1 + int((width - 1) * avail_space / actual_space)
                if new_width < width:
                    self.columns.width[i] = new_width
                    shrinked_columns[new_width] = i

        # Divide any remaining space among shrinked columns
        if shrinked_columns:
            extra = self._maxwidth - offset - sum(self.columns.width)
            actual_space = sum(shrinked_columns)

            if extra > 0:
                for i, width in enumerate(sorted(shrinked_columns)):
                    index = shrinked_columns[width]
                    extra_width = int(width * extra / actual_space)
                    self.columns.width[i] += extra_width
                    if i == (len(shrinked_columns) - 1):
                        extra = (
                            self._maxwidth - offset - sum(self.columns.width)
                        )
                        self.columns.width[index] += extra

        for i in range(len(self.columns)):
            self.columns.width[i] += pad_widths[i]

    @deprecated("1.0.0", "1.2.0", BTColumnCollection.padding.fget)
    def set_padding_widths(self, pad_width):  # pragma: no cover
        self.columns.padding_left = pad_width
        self.columns.padding_right = pad_width

    @deprecated("1.0.0", "1.2.0")
    def copy(self):
        return copy.copy(self)

    @deprecated_param("1.0.0", "1.2.0", "clear_metadata", "reset_columns")
    def clear(self, reset_columns=False, **kwargs):  # pragma: no cover
        """Clear the contents of the table.

        Clear all rows of the table, and if specified clears all column
        specific data.

        Parameters
        ----------
        reset_columns : bool, optional
            If it is true(default False), all metadata of columns such as their
            alignment, padding, width, etc. are also cleared and number of
            columns is set to 0.
        """
        kwargs.setdefault("clear_metadata", None)
        if kwargs["clear_metadata"]:
            reset_columns = kwargs["clear_metadata"]
        self.rows.clear()
        if reset_columns:
            self.columns.clear()

    def _get_horizontal_line(
        self, char, intersect_left, intersect_mid, intersect_right, mask=None
    ):
        """Get a horizontal line for the table.

        Internal method used to draw all horizontal lines in the table.
        Column width should be set prior to calling this method. This method
        detects intersection and handles it according to the values of
        `intersect_*_*` attributes.

        Parameters
        ----------
        char : str
            Character used to draw the line.

        Returns
        -------
        str
            String which will be printed as a line in the table.
        """
        width = self._width

        if mask is None:
            mask = [True] * len(self.columns)

        try:
            line = list(char * (int(width / termwidth(char)) + 1))[:width]
        except ZeroDivisionError:
            line = [" "] * width

        if len(line) == 0:
            return ""

        # Only if Special Intersection is enabled and horizontal line is
        # visible
        if not char.isspace():
            # If left border is enabled and it is visible
            visible_junc = not intersect_left.isspace()
            if termwidth(self.border.left) > 0:
                if not (self.border.left.isspace() and visible_junc):
                    length = min(
                        termwidth(self.border.left),
                        termwidth(intersect_left),
                    )
                    for i in range(length):
                        line[i] = intersect_left[i] if mask[0] else " "
            visible_junc = not intersect_right.isspace()
            # If right border is enabled and it is visible
            if termwidth(self.border.right) > 0:
                if not (self.border.right.isspace() and visible_junc):
                    length = min(
                        termwidth(self.border.right),
                        termwidth(intersect_right),
                    )
                    for i in range(length):
                        line[-i - 1] = (
                            intersect_right[-i - 1] if mask[-1] else " "
                        )
            visible_junc = not intersect_mid.isspace()
            # If column separator is enabled and it is visible
            if termwidth(self.columns.separator):
                if not (self.columns.separator.isspace() and visible_junc):
                    index = termwidth(self.border.left)
                    for i in range(len(self.columns) - 1):
                        if not mask[i]:
                            for j in range(self.columns.width[i]):
                                line[index + j] = " "
                        index += self.columns.width[i]
                        length = min(
                            termwidth(self.columns.separator),
                            termwidth(intersect_mid),
                        )
                        for j in range(length):
                            # TODO: we should also hide junctions based on mask
                            line[index + j] = (
                                intersect_mid[j]
                                if (mask[i] or mask[i + 1])
                                else " "
                            )
                        index += termwidth(self.columns.separator)

        return "".join(line)

    def _get_top_border(self, *args, **kwargs):
        return self._get_horizontal_line(
            self.border.top,
            self.border.top_left,
            self.border.top_junction,
            self.border.top_right,
            *args,
            **kwargs
        )

    def _get_header_separator(self, *args, **kwargs):
        return self._get_horizontal_line(
            self.columns.header.separator,
            self.border.header_left,
            self.columns.header.junction,
            self.border.header_right,
            *args,
            **kwargs
        )

    def _get_row_separator(self, *args, **kwargs):
        return self._get_horizontal_line(
            self.rows.separator,
            self.border.left_junction,
            self.junction,
            self.border.right_junction,
            *args,
            **kwargs
        )

    def _get_bottom_border(self, *args, **kwargs):
        return self._get_horizontal_line(
            self.border.bottom,
            self.border.bottom_left,
            self.border.bottom_junction,
            self.border.bottom_right,
            *args,
            **kwargs
        )

    @property
    def _width(self):
        """Get the actual width of the table as number of characters.

        Column width should be set prior to calling this method.

        Returns
        -------
        int
            Width of the table as number of characters.
        """
        if len(self.columns) == 0:
            return 0
        width = sum(self.columns.width)
        width += (len(self.columns) - 1) * termwidth(self.columns.separator)
        width += termwidth(self.border.left)
        width += termwidth(self.border.right)
        return width

    @deprecated("1.0.0", "1.2.0", _width.fget)
    def get_table_width(self):  # pragma: no cover
        return self._width

    def _get_string(self, rows=None, append=False, recalculate_width=True):
        row_header_visible = bool(
            "".join(
                x if x is not None else "" for x in self.rows.header
            ).strip()
        ) and (len(self.columns) > 0)

        column_header_visible = bool(
            "".join(
                x if x is not None else "" for x in self.columns.header
            ).strip()
        ) and (len(self.rows) > 0 or rows is not None)

        # Preparing table for printing serialno, row headers and column headers
        if len(self.columns) > 0:
            if self._serialno:
                self.columns.insert(
                    0, range(1, len(self.rows) + 1), self._serialno_header
                )

        if row_header_visible:
            self.columns.insert(0, self.rows.header)

        if column_header_visible:
            self.rows.insert(0, self.columns.header)

        if (self.columns._auto_width and recalculate_width) or sum(
            self.columns.width
        ) == 0:
            self._compute_width()

        try:
            # Rendering the top border
            if self.border.top:
                yield self._get_top_border()

            # Print column headers if not empty or only spaces
            row_iterator = iter(self.rows)
            if column_header_visible:
                yield next(row_iterator)._get_string(
                    align=self.columns.header.alignment
                )
                if self.columns.header.separator:
                    yield self._get_header_separator()

            # Printing rows
            first_row_encountered = False
            for i, row in enumerate(row_iterator):
                if first_row_encountered and self.rows.separator:
                    yield self._get_row_separator()
                first_row_encountered = True
                content = to_unicode(row)
                yield content

            if rows is not None:
                # Printing additional rows
                prev_length = len(self.rows)
                for i, row in enumerate(rows, start=1):
                    if first_row_encountered and self.rows.separator:
                        yield self._get_row_separator()
                    first_row_encountered = True
                    if self._serialno:
                        row.insert(0, prev_length + i)
                    if row_header_visible:
                        self.rows.append([None] + list(row))
                    else:
                        self.rows.append(row)
                    content = to_unicode(self.rows[-1])
                    if not append:
                        self.rows.pop()
                    yield content

            # Rendering the bottom border
            if self.border.bottom:
                yield self._get_bottom_border()
        except Exception:
            raise
        finally:
            # Cleanup
            if column_header_visible:
                self.rows.pop(0)

            if row_header_visible:
                self.columns.pop(0)

            if len(self.columns) > 0:
                if self._serialno:
                    self.columns.pop(0)
        return

    def stream(self, rows, append=False):
        """Get a generator for the table.

        This should be used in cases where data takes time to retrieve and it
        is required to be displayed as soon as possible. Any existing rows in
        the table shall also be returned. It is essential that atleast one of
        column header, width or existing rows set before calling this method.

        Parameters
        ----------
        rows : iterable
            A generator which yields one row at a time.

        append : bool, optional
            If rows should also be appended to the table.(Default False)

        Returns
        -------
        iterable:
            string representation of the table as a generators
        """
        for line in self._get_string(
            rows, append=append, recalculate_width=False
        ):
            yield line

    @deprecated("1.0.0", "1.2.0", str)
    def get_string(self):
        return str(self)

    def to_csv(self, file_name, *args, **kwargs):
        """Export table to CSV format.

        Parameters
        ----------
        file_name : str
            Path to CSV file.
        """

        if not isinstance(file_name, str):
            raise ValueError(
                ("Expected 'file_name' to be string, got {}").format(
                    type(file_name).__name__
                )
            )

        with open(file_name, mode="wt", newline="") as csv_file:
            csv_writer = csv.writer(csv_file, *args, **kwargs)
            if bool(
                "".join(
                    x if x is not None else "" for x in self.columns.header
                ).strip()
            ):
                csv_writer.writerow(self.columns.header)
            csv_writer.writerows(self.rows)

    def from_csv(self, file_name, header=True, **kwargs):
        """Create table from CSV file.

        Parameters
        ----------
        file_name : str
            Path to CSV file.
        header : bool, optional
            Whether First row in CSV file should be parsed as table header.

        Raises
        ------
        ValueError
            If `file_name` is not str type.
        FileNotFoundError
            If `file_name` is not valid path to file.
        """

        if not isinstance(file_name, str):
            raise ValueError(
                ("Expected 'file_name' to be string, got {}").format(
                    type(file_name).__name__
                )
            )

        with open(file_name, mode="rt", newline="") as csv_file:
            csv_reader = csv.reader(csv_file, **kwargs)

            if header:
                self.columns.header = next(csv_reader)
            for row in csv_reader:
                self.rows.append(row)
            return self
