import abc
import weakref


class BTBaseList(object, metaclass=abc.ABCMeta):
    def __init__(self, table, value):
        self._table = table
        self._value = self._validate(list(value))

    @property
    def _table(self):
        return self._table_ref()

    @_table.setter
    def _table(self, value):
        self._table_ref = weakref.ref(value)

    @property
    def value(self):
        return self._value

    def __len__(self):
        return len(self._value)

    def __iter__(self):
        return iter(self._value)

    def __next__(self):
        return next(self._value)

    def __repr__(self):
        class_ = type(self).__name__
        data = ", ".join(repr(v) for v in self._value)
        return "{}<{}>".format(class_, data)

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i, j in zip(self, other):
            if i != j:
                return False
        return True

    def __contains__(self, item):
        """Returns whether `item` is present"""
        return item in self._value

    def _append(self, item):
        self._value.append(item)

    def _insert(self, i, item):
        self._value.insert(i, item)

    def _pop(self, i=-1):
        return self._value.pop(self._get_canonical_key(i))

    def _remove(self, item):
        self._value.remove(item)

    def _reverse(self):
        self._value.reverse()

    def _sort(self, key, reverse=False):
        self._value.sort(key=key, reverse=reverse)

    def _clear(self):
        self._value.clear()

    def count(self, item):
        return self._value.count(item)

    def index(self, item, *args):
        """Returns the index of `item`"""
        try:
            return self._value.index(item, *args)
        except ValueError:
            raise KeyError("Key {} is not available".format(item))

    def __getitem__(self, key):
        """Returns item at index or header `key`"""
        return self._value[self._get_canonical_key(key)]

    def __setitem__(self, key, value):
        """Updates item at index or header `key`"""
        self._value[self._get_canonical_key(key)] = value

    def __delitem__(self, key):
        del self._value[self._get_canonical_key(key)]

    def _validate(self, value):
        if len(value) != self._get_ideal_length():
            raise ValueError(
                ("'Expected iterable of length {}, " "got {}").format(
                    self._get_ideal_length(), len(value)
                )
            )
        return value

    @abc.abstractmethod
    def _get_canonical_key(self, key):
        pass

    @abc.abstractmethod
    def _get_ideal_length(self):
        pass


class BTBaseRow(BTBaseList):
    def _get_canonical_key(self, key):
        return self._table.columns._canonical_key(key)

    def _get_ideal_length(self):
        return self._table._ncol

    def _validate(self, value):
        if self._get_ideal_length() == 0 and len(value) > 0:
            self._table.columns._reset_state(len(value))
        return super(BTBaseRow, self)._validate(value)


class BTBaseColumn(BTBaseList):
    def _get_canonical_key(self, key):
        return self._table.rows._canonical_key(key)

    def _get_ideal_length(self):
        return len(self._table._data)

    def _validate(self, value):
        if self._get_ideal_length() == 0 and len(value) > 0:
            self._table.rows._reset_state(len(value))
        return super(BTBaseColumn, self)._validate(value)
