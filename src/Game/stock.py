import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

class Stock:
    BONUS_PATH = os.path.join(dir_path, "BONUS.json")
    STOCK_PRICE_PATH = os.path.join(dir_path, "STOCK_PRICE.json")

    def __init__(self, name):
        with open(self.STOCK_PRICE_PATH, "r") as f:
            self.stock_prices = json.load(f)
        with open(self.BONUS_PATH, "r") as f:
            self.bonuses = json.load(f)

        self.name = name
        self.specific_stock_price_info = self.stock_prices[self.name]
        self.specific_bonus_info = self.bonuses[self.name]

        self.number = 0
        self.current_price = None
        self.current_bonus = None

    def set_current_info(self, number):
        if number < 2:
            raise Exception("Something's wrong")
        
        self.current_price = self.specific_stock_price_info[str(number)]
        self.current_bonus = self.specific_bonus_info[str(number)]
        self.number = number


