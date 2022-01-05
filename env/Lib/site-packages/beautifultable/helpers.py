import copy
import weakref
import operator

from . import enums
from .base import BTBaseRow, BTBaseColumn
from .utils import pre_process, termwidth, textwrap, ensure_type
from .compat import basestring, Iterable, to_unicode, zip_longest
from .meta import AlignmentMetaData, NonNegativeIntegerMetaData


class BTRowHeader(BTBaseColumn):
    def __init__(self, table, value):
        for i in value:
            self._validate_item(i)
        super(BTRowHeader, self).__init__(table, value)

    def __setitem__(self, key, value):
        self._validate_item(value)
        super(BTRowHeader, self).__setitem__(key, value)

    def _validate_item(self, value):
        if not (isinstance(value, basestring) or value is None):
            raise TypeError(
                ("header must be of type 'str', " "got {}").format(
                    type(value).__name__
                )
            )


class BTColumnHeader(BTBaseRow):
    def __init__(self, table, value):
        for i in value:
            self._validate_item(i)
        super(BTColumnHeader, self).__init__(table, value)
        self.alignment = None

    @property
    def alignment(self):
        """get/set alignment of the column header of the table.

        It can be any iterable containing only the following:

        * beautifultable.ALIGN_LEFT
        * beautifultable.ALIGN_CENTER
        * beautifultable.ALIGN_RIGHT
        """
        return self._alignment

    @alignment.setter
    def alignment(self, value):
        if value is None:
            self._alignment = None
            return
        if isinstance(value, enums.Alignment):
            value = [value] * len(self)
        self._alignment = AlignmentMetaData(self._table, value)

    @property
    def separator(self):
        """Character used to draw the line seperating header from the table."""
        return self._table._header_separator

    @separator.setter
    def separator(self, value):
        self._table._header_separator = ensure_type(value, basestring)

    @property
    def junction(self):
        """Character used to draw junctions in the header separator."""
        return self._table._header_junction

    @junction.setter
    def junction(self, value):
        self._table._header_junction = ensure_type(value, basestring)

    def __setitem__(self, key, value):
        self._validate_item(value)
        super(BTColumnHeader, self).__setitem__(key, value)

    def _validate_item(self, value):
        if not (isinstance(value, basestring) or value is None):
            raise TypeError(
                ("header must be of type 'str', " "got {}").format(
                    type(value).__name__
                )
            )


class BTRowData(BTBaseRow):
    def _get_padding(self):
        return (
            self._table.columns.padding_left,
            self._table.columns.padding_right,
        )

    def _clamp_row(self, row):
        """Process a row so that it is clamped by column_width.

        Parameters
        ----------
        row : array_like
             A single row.

        Returns
        -------
        list of list:
            List representation of the `row` after it has been processed
            according to width exceed policy.
        """
        table = self._table
        lpw, rpw = self._get_padding()
        wep = table.columns.width_exceed_policy

        result = []

        if (
            wep is enums.WidthExceedPolicy.WEP_STRIP
            or wep is enums.WidthExceedPolicy.WEP_ELLIPSIS
        ):

            # Let's strip the row
            delimiter = (
                "" if wep is enums.WidthExceedPolicy.WEP_STRIP else "..."
            )
            row_item_list = []
            for index, row_item in enumerate(row):
                left_pad = table.columns._pad_character * lpw[index]
                right_pad = table.columns._pad_character * rpw[index]
                clmp_str = (
                    left_pad
                    + self._clamp_string(row_item, index, delimiter)
                    + right_pad
                )
                row_item_list.append(clmp_str)
            result.append(row_item_list)
        elif wep is enums.WidthExceedPolicy.WEP_WRAP:

            # Let's wrap the row
            string_partition = []

            for index, row_item in enumerate(row):
                width = table.columns.width[index] - lpw[index] - rpw[index]
                string_partition.append(textwrap(row_item, width))

            for row_items in zip_longest(*string_partition, fillvalue=""):
                row_item_list = []
                for index, row_item in enumerate(row_items):
                    left_pad = table.columns._pad_character * lpw[index]
                    right_pad = table.columns._pad_character * rpw[index]
                    row_item_list.append(left_pad + row_item + right_pad)
                result.append(row_item_list)

        return [[""] * len(table.columns)] if len(result) == 0 else result

    def _clamp_string(self, row_item, index, delimiter=""):
        """Clamp `row_item` to fit in column referred by index.

        This method considers padding and appends the delimiter if `row_item`
        needs to be truncated.

        Parameters
        ----------
        row_item: str
            String which should be clamped.

        index: int
            Index of the column `row_item` belongs to.

        delimiter: str
            String which is to be appended to the clamped string.

        Returns
        -------
        str
            The modified string which fits in it's column.
        """
        lpw, rpw = self._get_padding()
        width = self._table.columns.width[index] - lpw[index] - rpw[index]

        if termwidth(row_item) <= width:
            return row_item
        else:
            if width - len(delimiter) >= 0:
                clamped_string = (
                    textwrap(row_item, width - len(delimiter))[0] + delimiter
                )
            else:
                clamped_string = delimiter[:width]
            return clamped_string

    def _get_string(
        self,
        align=None,
        mask=None,
        draw_left_border=True,
        draw_right_border=True,
    ):
        """Return a string representation of a row."""

        rows = []

        table = self._table
        width = table.columns.width
        sign = table.sign

        if align is None:
            align = table.columns.alignment

        if mask is None:
            mask = [True] * len(table.columns)

        lpw, rpw = self._get_padding()

        string = []
        for i, item in enumerate(self._value):
            if isinstance(item, type(table)):
                # temporarily change the max width of the table
                curr_maxwidth = item.maxwidth
                item.maxwidth = width[i] - lpw[i] - rpw[i]
                rows.append(
                    pre_process(
                        item,
                        table.detect_numerics,
                        table.precision,
                        sign.value,
                    ).split("\n")
                )
                item.maxwidth = curr_maxwidth
            else:
                rows.append(
                    pre_process(
                        item,
                        table.detect_numerics,
                        table.precision,
                        sign.value,
                    ).split("\n")
                )
        for row in map(list, zip_longest(*rows, fillvalue="")):
            for i in range(len(row)):
                row[i] = pre_process(
                    row[i],
                    table.detect_numerics,
                    table.precision,
                    sign.value,
                )
            for row_ in self._clamp_row(row):
                for i in range(len(table.columns)):
                    # str.format method doesn't work for multibyte strings
                    # hence, we need to manually align the texts instead
                    # of using the align property of the str.format method
                    pad_len = width[i] - termwidth(row_[i])
                    if align[i].value == "<":
                        right_pad = " " * pad_len
                        row_[i] = to_unicode(row_[i]) + right_pad
                    elif align[i].value == ">":
                        left_pad = " " * pad_len
                        row_[i] = left_pad + to_unicode(row_[i])
                    else:
                        left_pad = " " * (pad_len // 2)
                        right_pad = " " * (pad_len - pad_len // 2)
                        row_[i] = left_pad + to_unicode(row_[i]) + right_pad
                content = []
                for j, item in enumerate(row_):
                    if j > 0:
                        content.append(
                            table.columns.separator
                            if (mask[j - 1] or mask[j])
                            else " " * termwidth(table.columns.separator)
                        )
                    content.append(item)
                content = "".join(content)
                content = (
                    table.border.left
                    if mask[0]
                    else " " * termwidth(table.border.left)
                ) + content
                content += (
                    table.border.right
                    if mask[-1]
                    else " " * termwidth(table.border.right)
                )
                string.append(content)
        return "\n".join(string)

    def __str__(self):
        return self._get_string()


class BTColumnData(BTBaseColumn):
    pass


class BTRowCollection(object):
    def __init__(self, table):
        self._table = table
        self._reset_state(0)

    @property
    def _table(self):
        return self._table_ref()

    @_table.setter
    def _table(self, value):
        self._table_ref = weakref.ref(value)

    def _reset_state(self, nrow):
        self._table._data = type(self._table._data)(
            self._table,
            [
                BTRowData(self._table, [None] * self._table._ncol)
                for i in range(nrow)
            ],
        )
        self.header = BTRowHeader(self._table, [None] * nrow)

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, value):
        self._header = BTRowHeader(self._table, value)

    @property
    def separator(self):
        """Character used to draw the line seperating two rows."""
        return self._table._row_separator

    @separator.setter
    def separator(self, value):
        self._table._row_separator = ensure_type(value, basestring)

    def _canonical_key(self, key):
        if isinstance(key, (int, slice)):
            return key
        elif isinstance(key, basestring):
            return self.header.index(key)
        raise TypeError(
            ("row indices must be int, str or slices, not {}").format(
                type(key).__name__
            )
        )

    def __len__(self):
        return len(self._table._data)

    def __getitem__(self, key):
        """Get a particular row, or a new table by slicing.

        Parameters
        ----------
        key : int, slice, str
            If key is an `int`, returns a row at index `key`.
            If key is an `str`, returns the first row with heading `key`.
            If key is a slice object, returns a new sliced table.

        Raises
        ------
        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` index is out of range.
        KeyError
            If `str` key is not found in header.
        """
        if isinstance(key, slice):
            new_table = copy.deepcopy(self._table)
            new_table.rows.clear()
            new_table.rows.header = self._table.rows.header[key]
            for i, r in enumerate(self._table._data[key]):
                new_table.rows[i] = r.value
            return new_table
        if isinstance(key, (int, basestring)):
            return self._table._data[key]
        raise TypeError(
            ("row indices must be int, str or a slice object, not {}").format(
                type(key).__name__
            )
        )

    def __delitem__(self, key):
        """Delete a row, or multiple rows by slicing.

        Parameters
        ----------
        key : int, slice, str
            If key is an `int`, deletes a row at index `key`.
            If key is an `str`, deletes the first row with heading `key`.
            If key is a slice object, deletes multiple rows.

        Raises
        ------
        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        KeyError
            If `str` key is not in header.
        """
        if isinstance(key, (int, basestring, slice)):
            del self._table._data[key]
            del self.header[key]
        else:
            raise TypeError(
                (
                    "row indices must be int, str or " "a slice object, not {}"
                ).format(type(key).__name__)
            )

    def __setitem__(self, key, value):
        """Update a row, or multiple rows by slicing.

        Parameters
        ----------
        key : int, slice, str
            If key is an `int`, updates a row.
            If key is an `str`, updates the first row with heading `key`.
            If key is a slice object, updates multiple rows.

        Raises
        ------
        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        KeyError
            If `str` key is not in header.
        """
        if isinstance(key, (int, basestring)):
            self._table._data[key] = BTRowData(self._table, value)
        elif isinstance(key, slice):
            value = [list(row) for row in value]
            if len(self._table.columns) == 0:
                self._table.columns._initialize(len(value[0]))
            self._table._data[key] = [
                BTRowData(self._table, row) for row in value
            ]
        else:
            raise TypeError("key must be int, str or a slice object")

    def __contains__(self, key):
        if isinstance(key, basestring):
            return key in self.header
        elif isinstance(key, Iterable):
            return key in self._table._data
        else:
            raise TypeError(
                ("'key' must be str or Iterable, " "not {}").format(
                    type(key).__name__
                )
            )

    def __iter__(self):
        return BTCollectionIterator(self)

    def __repr__(self):
        return repr(self._table._data)

    def __str__(self):
        return str(self._table._data)

    def reverse(self):
        """Reverse the table row-wise *IN PLACE*."""
        self._table._data._reverse()

    def pop(self, index=-1):
        """Remove and return row at index (default last).

        Parameters
        ----------
        index : int, str
            index or heading of the row. Normal list rules apply.
        """
        if not isinstance(index, (int, basestring)):
            raise TypeError(
                ("row index must be int or str, " "not {}").format(
                    type(index).__name__
                )
            )
        if len(self._table._data) == 0:
            raise IndexError("pop from empty table")
        else:
            res = self._table._data._pop(index)
            self.header._pop(index)
            return res

    def insert(self, index, row, header=None):
        """Insert a row before index in the table.

        Parameters
        ----------
        index : int
            List index rules apply

        row : iterable
            Any iterable of appropriate length.

        header : str, optional
            Heading of the row

        Raises
        ------
        TypeError:
            If `row` is not an iterable.

        ValueError:
            If size of `row` is inconsistent with the current number
            of columns.
        """
        if self._table._ncol == 0:
            row = list(row)
            self._table.columns._reset_state(len(row))
        self.header._insert(index, header)
        self._table._data._insert(index, BTRowData(self._table, row))

    def append(self, row, header=None):
        """Append a row to end of the table.

        Parameters
        ----------
        row : iterable
            Any iterable of appropriate length.

        header : str, optional
            Heading of the row

        """
        self.insert(len(self), row, header)

    def update(self, key, value):
        """Update row(s) identified with `key` in the table.

        `key` can be a index or a slice object.

        Parameters
        ----------
        key : int or slice
            index of the row, or a slice object.

        value : iterable
            If an index is specified, `value` should be an iterable
            of appropriate length. Instead if a slice object is
            passed as key, value should be an iterable of rows.

        Raises
        ------
        IndexError:
            If index specified is out of range.

        TypeError:
            If `value` is of incorrect type.

        ValueError:
            If length of row does not matches number of columns.
        """
        self[key] = value

    def clear(self):
        self._reset_state(0)

    def sort(self, key, reverse=False):
        """Stable sort of the table *IN-PLACE* with respect to a column.

        Parameters
        ----------
        key: int, str
            index or header of the column. Normal list rules apply.
        reverse : bool
            If `True` then table is sorted as if each comparison was reversed.
        """
        if isinstance(key, (int, basestring)):
            key = operator.itemgetter(key)
        elif callable(key):
            pass
        else:
            raise TypeError(
                "'key' must either be 'int' or 'str' or a 'callable'"
            )

        indices = sorted(
            range(len(self)),
            key=lambda x: key(self._table._data[x]),
            reverse=reverse,
        )
        self._table._data._sort(key=key, reverse=reverse)
        self.header = [self.header[i] for i in indices]

    def filter(self, key):
        """Return a copy of the table with only those rows which satisfy a
        certain condition.

        Returns
        -------
        BeautifulTable:
            Filtered copy of the BeautifulTable instance.
        """
        new_table = self._table.rows[:]
        new_table.rows.clear()
        for row in filter(key, self):
            new_table.rows.append(row)
        return new_table


class BTCollectionIterator(object):
    def __init__(self, collection):
        self._collection = collection
        self._index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self._index += 1
        if self._index == len(self._collection):
            raise StopIteration
        return self._collection[self._index]


class BTColumnCollection(object):
    def __init__(self, table, default_alignment, default_padding):
        self._table = table
        self._width_exceed_policy = enums.WEP_WRAP
        self._pad_character = " "
        self.default_alignment = default_alignment
        self.default_padding = default_padding

        self._reset_state(0)

    @property
    def _table(self):
        return self._table_ref()

    @_table.setter
    def _table(self, value):
        self._table_ref = weakref.ref(value)

    @property
    def padding(self):
        """Set width for left and rigth padding of the columns of the table."""
        raise AttributeError(
            "cannot read attribute 'padding'. use 'padding_{left|right}'"
        )

    @padding.setter
    def padding(self, value):
        self.padding_left = value
        self.padding_right = value

    def _reset_state(self, ncol):
        self._table._ncol = ncol
        self._header = BTColumnHeader(self._table, [None] * ncol)
        self._auto_width = True
        self._alignment = AlignmentMetaData(
            self._table, [self.default_alignment] * ncol
        )
        self._width = NonNegativeIntegerMetaData(self._table, [0] * ncol)
        self._padding_left = NonNegativeIntegerMetaData(
            self._table, [self.default_padding] * ncol
        )
        self._padding_right = NonNegativeIntegerMetaData(
            self._table, [self.default_padding] * ncol
        )
        self._table._data = type(self._table._data)(
            self._table,
            [
                BTRowData(self._table, [None] * ncol)
                for i in range(len(self._table._data))
            ],
        )

    def _canonical_key(self, key):
        if isinstance(key, (int, slice)):
            return key
        elif isinstance(key, basestring):
            return self.header.index(key)
        raise TypeError(
            ("column indices must be int, str or slices, not {}").format(
                type(key).__name__
            )
        )

    @property
    def header(self):
        """get/set headings for the columns of the table.

        It can be any iterable with all members an instance of `str` or None.
        """
        return self._header

    @header.setter
    def header(self, value):
        self._header = BTColumnHeader(self._table, value)

    @property
    def alignment(self):
        """get/set alignment of the columns of the table.

        It can be any iterable containing only the following:

        * beautifultable.ALIGN_LEFT
        * beautifultable.ALIGN_CENTER
        * beautifultable.ALIGN_RIGHT
        """
        return self._alignment

    @alignment.setter
    def alignment(self, value):
        if isinstance(value, enums.Alignment):
            value = [value] * len(self)
        self._alignment = AlignmentMetaData(self._table, value)

    @property
    def width(self):
        """get/set width for the columns of the table.

        Width of the column specifies the max number of characters
        a column can contain. Larger characters are handled according to
        `width_exceed_policy`. This can be one of `'auto'`, a non-negative
        integer or an iterable of the same length as the number of columns.
        If set to anything other than 'auto', the user is responsible for
        updating it if new columns are added or existing ones are updated.
        """
        return self._width

    @width.setter
    def width(self, value):
        if isinstance(value, str):
            if value == "auto":
                self._auto_width = True
                return
            raise ValueError("Invalid value '{}'".format(value))
        if isinstance(value, int):
            value = [value] * len(self)
        self._width = NonNegativeIntegerMetaData(self._table, value)
        self._auto_width = False

    @property
    def padding_left(self):
        """get/set width for left padding of the columns of the table.

        Left Width of the padding specifies the number of characters
        on the left of a column reserved for padding. By Default It is 1.
        """
        return self._padding_left

    @padding_left.setter
    def padding_left(self, value):
        if isinstance(value, int):
            value = [value] * len(self)
        self._padding_left = NonNegativeIntegerMetaData(self._table, value)

    @property
    def padding_right(self):
        """get/set width for right padding of the columns of the table.

        Right Width of the padding specifies the number of characters
        on the rigth of a column reserved for padding. By default It is 1.
        """
        return self._padding_right

    @padding_right.setter
    def padding_right(self, value):
        if isinstance(value, int):
            value = [value] * len(self)
        self._padding_right = NonNegativeIntegerMetaData(self._table, value)

    @property
    def width_exceed_policy(self):
        """Attribute to control how exceeding column width should be handled.

        It can be one of the following:

        ============================  =========================================
         Option                        Meaning
        ============================  =========================================
         beautifulbable.WEP_WRAP       An item is wrapped so every line fits
                                       within it's column width.

         beautifultable.WEP_STRIP      An item is stripped to fit in it's
                                       column.

         beautifultable.WEP_ELLIPSIS   An item is stripped to fit in it's
                                       column and appended with ...(Ellipsis).
        ============================  =========================================
        """
        return self._width_exceed_policy

    @width_exceed_policy.setter
    def width_exceed_policy(self, value):
        if not isinstance(value, enums.WidthExceedPolicy):
            allowed = (
                "{}.{}".format(type(self).__name__, i.name)
                for i in enums.WidthExceedPolicy
            )
            error_msg = (
                "allowed values for width_exceed_policy are: "
                + ", ".join(allowed)
            )
            raise ValueError(error_msg)
        self._width_exceed_policy = value

    @property
    def default_alignment(self):
        """Attribute to control the alignment of newly created columns.

        It can be one of the following:

        ============================  =========================================
         Option                        Meaning
        ============================  =========================================
         beautifultable.ALIGN_LEFT     New columns are left aligned.

         beautifultable.ALIGN_CENTER   New columns are center aligned.

         beautifultable.ALIGN_RIGHT    New columns are right aligned.
        ============================  =========================================
        """
        return self._default_alignment

    @default_alignment.setter
    def default_alignment(self, value):
        if not isinstance(value, enums.Alignment):
            allowed = (
                "{}.{}".format(type(self).__name__, i.name)
                for i in enums.Alignment
            )
            error_msg = (
                "allowed values for default_alignment are: "
                + ", ".join(allowed)
            )
            raise ValueError(error_msg)
        self._default_alignment = value

    @property
    def default_padding(self):
        """Initial value for Left and Right padding widths for new columns."""
        return self._default_padding

    @default_padding.setter
    def default_padding(self, value):
        if not isinstance(value, int):
            raise TypeError("default_padding must be an integer")
        elif value < 0:
            raise ValueError("default_padding must be a non-negative integer")
        else:
            self._default_padding = value

    @property
    def separator(self):
        """Character used to draw the line seperating two columns."""
        return self._table._column_separator

    @separator.setter
    def separator(self, value):
        self._table._column_separator = ensure_type(value, basestring)

    def __len__(self):
        return self._table._ncol

    def __getitem__(self, key):
        """Get a column, or a new table by slicing.

        Parameters
        ----------

        key : int, slice, str
            If key is an `int`, returns column at index `key`.
            If key is an `str`, returns first column with heading `key`.
            If key is a slice object, returns a new sliced table.

        Raises
        ------

        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        KeyError
            If `str` key is not in header.
        """
        if isinstance(key, int):
            pass
        elif isinstance(key, slice):
            new_table = copy.deepcopy(self._table)

            new_table.columns.clear()
            new_table.columns.header = self.header[key]
            new_table.columns.alignment = self.alignment[key]
            new_table.columns.padding_left = self.padding_left[key]
            new_table.columns.padding_right = self.padding_right[key]
            new_table.columns.width = self.width[key]
            new_table.columns._auto_width = self._auto_width
            for i, r in enumerate(self._table._data):
                new_table.rows[i] = r.value[key]
            return new_table
        elif isinstance(key, basestring):
            key = self.header.index(key)
        else:
            raise TypeError(
                (
                    "column indices must be integers, strings or "
                    "slices, not {}"
                ).format(type(key).__name__)
            )
        return BTColumnData(
            self._table, [row[key] for row in self._table._data]
        )

    def __delitem__(self, key):
        """Delete a column, or multiple columns by slicing.

        Parameters
        ----------

        key : int, slice, str
            If key is an `int`, deletes column at index `key`.
            If key is a slice object, deletes multiple columns.
            If key is an `str`, deletes the first column with heading `key`

        Raises
        ------

        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        KeyError
            If `str` key is not in header.
        """
        if isinstance(key, (int, basestring, slice)):
            key = self._canonical_key(key)

            del self.alignment[key]
            del self.width[key]
            del self.padding_left[key]
            del self.padding_right[key]
            for row in self._table.rows:
                del row[key]
            del self.header[key]
            if self.header.alignment is not None:
                del self.header.alignment[key]
            self._table._ncol = len(self.header)
            if self._table._ncol == 0:
                del self._table.rows[:]
        else:
            raise TypeError(
                ("table indices must be int, str or " "slices, not {}").format(
                    type(key).__name__
                )
            )

    def __setitem__(self, key, value):
        """Update a column, or multiple columns by slicing.

        Parameters
        ----------

        key : int, slice, str
            If key is an `int`, updates column at index `key`.
            If key is an `str`, updates first column with heading `key`.
            If key is a slice object, updates multiple columns.

        Raises
        ------

        TypeError
            If key is not of type int, slice or str.
        IndexError
            If `int` key is out of range.
        KeyError
            If `str` key is not in header
        """
        if not isinstance(key, (int, basestring, slice)):
            raise TypeError(
                "column indices must be of type int, str or a slice object"
            )
        for row, new_item in zip(self._table.rows, value):
            row[key] = new_item

    def __contains__(self, key):
        if isinstance(key, basestring):
            return key in self.header
        elif isinstance(key, Iterable):
            key = list(key)
            return any(key == column for column in self)
        else:
            raise TypeError(
                ("'key' must be str or Iterable, " "not {}").format(
                    type(key).__name__
                )
            )

    def __iter__(self):
        return BTCollectionIterator(self)

    def __repr__(self):
        return repr(self._table)

    def __str__(self):
        return str(self._table._data)

    def clear(self):
        self._reset_state(0)

    def pop(self, index=-1):
        """Remove and return column at index (default last).

        Parameters
        ----------
        index : int, str
            index of the column, or the header of the column.
            If index is specified, then normal list rules apply.

        Raises
        ------
        TypeError:
            If index is not an instance of `int`, or `str`.

        IndexError:
            If Table is empty.
        """
        if not isinstance(index, (int, basestring)):
            raise TypeError(
                ("column index must be int or str, " "not {}").format(
                    type(index).__name__
                )
            )
        if self._table._ncol == 0:
            raise IndexError("pop from empty table")
        else:
            res = []
            index = self._canonical_key(index)
            for row in self._table.rows:
                res.append(row._pop(index))
            res = BTColumnData(self._table, res)
            self.alignment._pop(index)
            self.width._pop(index)
            self.padding_left._pop(index)
            self.padding_right._pop(index)
            self.header._pop(index)

            self._table._ncol = len(self.header)
            if self._table._ncol == 0:
                del self._table.rows[:]
            return res

    def update(self, key, value):
        """Update a column named `header` in the table.

        If length of column is smaller than number of rows, lets say
        `k`, only the first `k` values in the column is updated.

        Parameters
        ----------
        key : int, str
            If `key` is int, column at index `key` is updated.
            If `key` is str, the first column with heading `key` is updated.

        value : iterable
            Any iterable of appropriate length.

        Raises
        ------
        TypeError:
            If length of `column` is shorter than number of rows.

        ValueError:
            If no column exists with heading `header`.
        """
        self[key] = value

    def insert(
        self,
        index,
        column,
        header=None,
        padding_left=None,
        padding_right=None,
        alignment=None,
    ):
        """Insert a column before `index` in the table.

        If length of column is bigger than number of rows, lets say
        `k`, only the first `k` values of `column` is considered.
        If column is shorter than 'k', ValueError is raised.

        Note that Table remains in consistent state even if column
        is too short. Any changes made by this method is rolled back
        before raising the exception.

        Parameters
        ----------
        index : int
            List index rules apply.

        column : iterable
            Any iterable of appropriate length.

        header : str, optional
            Heading of the column.

        padding_left : int, optional
            Left padding of the column.

        padding_right : int, optional
            Right padding of the column.

        alignment : Alignment, optional
            alignment of the column.

        Raises
        ------
        TypeError:
            If `header` is not of type `str`.

        ValueError:
            If length of `column` is shorter than number of rows.
        """
        padding_left = (
            self.default_padding if padding_left is None else padding_left
        )
        padding_right = (
            self.default_padding if padding_right is None else padding_right
        )
        alignment = self.default_alignment if alignment is None else alignment
        if not isinstance(padding_left, int):
            raise TypeError(
                "'padding_left' should be of type 'int' not '{}'".format(
                    type(padding_left).__name__
                )
            )
        if not isinstance(padding_right, int):
            raise TypeError(
                "'padding_right' should be of type 'int' not '{}'".format(
                    type(padding_right).__name__
                )
            )
        if not isinstance(alignment, enums.Alignment):
            raise TypeError(
                "alignment should be of type '{}' not '{}'".format(
                    enums.Alignment.__name__, type(alignment).__name__
                )
            )

        if self._table._ncol == 0:
            self.header = [header]
            self.padding_left = [padding_left]
            self.padding_right = [padding_right]
            self.alignment = [alignment]
            self._table._data = type(self._table._data)(
                self._table, [BTRowData(self._table, [i]) for i in column]
            )
        else:
            if (not isinstance(header, basestring)) and (header is not None):
                raise TypeError(
                    "header must be of type 'str' not '{}'".format(
                        type(header).__name__
                    )
                )
            column_length = 0
            for row, new_item in zip(self._table.rows, column):
                row._insert(index, new_item)
                column_length += 1
            if column_length == len(self._table.rows):
                self._table._ncol += 1
                self.header._insert(index, header)
                self.width._insert(index, 0)
                self.alignment._insert(index, alignment)
                self.padding_left._insert(index, padding_left)
                self.padding_right._insert(index, padding_right)
                if self.header.alignment is not None:
                    self.header.alignment._insert(index, alignment)
            else:
                # Roll back changes so that table remains in consistent state
                for j in range(column_length, -1, -1):
                    self._table.rows[j]._pop(index)
                raise ValueError(
                    (
                        "length of 'column' should be atleast {}, " "got {}"
                    ).format(len(self._table.rows), column_length)
                )

    def append(
        self,
        column,
        header=None,
        padding_left=None,
        padding_right=None,
        alignment=None,
    ):
        """Append a column to end of the table.

        Parameters
        ----------
        column : iterable
            Any iterable of appropriate length.

        header : str, optional
            Heading of the column

        padding_left : int, optional
            Left padding of the column

        padding_right : int,  optional
            Right padding of the column

        alignment : Alignment, optional
            alignment of the column
        """
        self.insert(
            self._table._ncol,
            column,
            header,
            padding_left,
            padding_right,
            alignment,
        )
