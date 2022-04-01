from shop.shopper_base import ShopperBase


class CharsiShopper(ShopperBase):

    def __init__(self):
        return

    def get_name(self):
        return "Charsi"

    def run(self):
        Logger.info(f"Personal {self.get_name()} Shopper at your service! Hang on, running some errands...")
        self.reset_shop()
        self.shop_loop()