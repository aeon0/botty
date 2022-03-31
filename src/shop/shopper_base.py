import abc


class ShopperBase(abc.ABC):

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def run(self):
        pass


ShopperBase.register(tuple)

assert issubclass(tuple, ShopperBase)
assert isinstance((), ShopperBase)
