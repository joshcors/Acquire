import os

dir_path = os.path.dirname(os.path.realpath(__file__))

class Player:
    def __init__(self, name):
        self.name = name

        self.money = 6000

        with open(os.path.join(dir_path, "stock_names.txt"), "r") as f:
            stock_names = f.read().splitlines()

        self.stocks = {name : 0 for name in stock_names}

        self.tiles = []

    def add_tile(self, tile):
        self.tiles.append(tile)

    def replace_tile(self, old_tile, new_tile):
        self.tiles[self.tiles.index(old_tile)] = new_tile

    def get_new_chain_decision(self, options):
        first_letters = [option[0] for option in options]
        display_options = [f"({letter}){option[1:]}" for letter, option in zip(first_letters, options)]
        result = input(f"Choose new chain ({display_options}): ")
        while result not in options and result not in first_letters:
            print("Invalid")
            result = input(f"Choose new chain ({display_options}): ")

        if result in first_letters:
            result = options[first_letters.index(result)]

        return result
    
    def get_merger_decision(self, options):
        first_letters = [option[0] for option in options]
        display_options = [f"({letter}){option[1:]}" for letter, option in zip(first_letters, options)]
        result = input(f"Choose merger survivor ({display_options}): ")
        while result not in options and result not in first_letters:
            print("Invalid")
            result = input(f"Choose merger survivor ({display_options}): ")

        if result in first_letters:
            result = options[first_letters.index(result)]

        return result
    
    def get_tile_selection(self):
        result = input(f"Choose tile to place ({self.tiles}): ")
        while result not in self.tiles:
            print("Invalid")
            result = input(f"Choose tile to place ({self.tiles}): ")

        self.tiles.pop(self.tiles.index(result))

        return result

    def get_buy_selections(self, options):
        first_letters = [option[0] for option in options]
        display_options = [f"({letter}){option[1:]}" for letter, option in zip(first_letters, options)]
        result = input(f"Enter all stocks to purchase ({display_options}): ").strip().split(' ')
        result_good = [val in first_letters or val in options for val in result]
        while not all(result_good):
            print("Invalid")
            result = input(f"Enter all stocks to purchase ({display_options}): ").strip().split(' ')
            result_good = [val in first_letters or val in options for val in result]

        for i, val in enumerate(result):
            if val in first_letters: 
                result[i] = options[first_letters.index(val)]

        return result
    
    def buy_stock(self, names, counts, stock_prices):
        total_expenditure = 0
        for count, price in zip(counts, stock_prices):
            total_expenditure += count * price

        if total_expenditure > self.money:
            # Change to sending warning message, not raising exception
            raise Exception("Cannot spend more money than you have")
        
        self.money -= total_expenditure
        for name, count in zip(names, counts):
            self.stocks[name] += count

    def two_for_one(self, defunct_stock_name, new_stock_name, number_defunct_stock):
        if number_defunct_stock % 2 != 0:
            raise Exception("Can't 2-for-1 an odd number")
        
        number_new_stock = number_defunct_stock // 2

        self.stocks[defunct_stock_name] -= number_defunct_stock
        self.stocks[new_stock_name] += number_new_stock

    def sell_stock(self, names, counts, stock_prices):
        total_revenue = 0
        for count, price in zip(counts, stock_prices):
            total_revenue += count * price

        self.money += total_revenue

        for name, count in zip(names, counts):
            self.stocks[name] -= count
        


