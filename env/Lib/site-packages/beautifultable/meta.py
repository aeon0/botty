from .base import BTBaseRow
from .enums import Alignment


class MetaData(BTBaseRow):
    def __init__(self, table, row):
        for i in row:
            self.validate(i)
        super(MetaData, self).__init__(table, row)

    def __setitem__(self, key, value):
        self.validate(value)
        super(MetaData, self).__setitem__(key, value)

    def validate(self, value):
        pass


class AlignmentMetaData(MetaData):
    def validate(self, value):
        if not isinstance(value, Alignment):
            allowed = (
                "{}.{}".format(type(self).__name__, i.name) for i in Alignment
            )
            error_msg = (
                "allowed values for alignment are: "
                + ", ".join(allowed)
                + ", was {}".format(value)
            )
            raise TypeError(error_msg)


class NonNegativeIntegerMetaData(MetaData):
    def validate(self, value):
        if isinstance(value, int) and value >= 0:
            pass
        else:
            raise TypeError(
                ("Value must a non-negative integer, " "was {}").format(value)
            )
