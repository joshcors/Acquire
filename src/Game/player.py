import os
import uuid
import locale
locale.setlocale( locale.LC_ALL, '' )

dir_path = os.path.dirname(os.path.realpath(__file__))

class Player:
    def __init__(self, name):
        self.name = name
        self.uuid = uuid.uuid4()

        self.money = 6000

        with open(os.path.join(dir_path, "stock_names.txt"), "r") as f:
            stock_names = f.read().splitlines()

        self.stocks = {name : 0 for name in stock_names}

        self.tiles = []

    def my_str(self):
        stock_names = list(self.stocks.keys())
        max_len = max([len(name) for name in stock_names]) + 2
        width = len(stock_names) * (max_len + 1) + 1

        s = '-' * width + '\n'
        s += '|' + '|'.join([name.center(max_len) for name in stock_names]) + '|' + "\n"
        s += '-' * width + '\n'
        s += '|' + '|'.join([str(self.stocks[name]).center(max_len) for name in stock_names]) + '|' + "\n"
        s += '-' * width + '\n\n'

        s += f"Money: {locale.currency(self.money, grouping=True)}" + '\n\n'

        s += ' '.join(["------", ] * len(self.tiles)) + '\n'
        s += ' '.join(["|" + str(tile).center(4) + "|" for tile in self.tiles]) + '\n'
        s += ' '.join(["------", ] * len(self.tiles)) + '\n'

        return s

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
    
    def handle_tile_selection(self, tile):
        try:
            self.tiles.pop(self.tiles.index(tile))
            return True
        except:
            return False
            

    def get_tile_selection(self):
        result = input(f"Choose tile to place ({self.tiles}): ")
        while result not in self.tiles:
            print("Invalid")
            result = input(f"Choose tile to place ({self.tiles}): ")

        self.tiles.pop(self.tiles.index(result))

        return result

    def get_buy_selections(self, options, stock_names, stocks_remaining):
        first_letters = [option[0] for option in options]
        display_options = [f"({letter}){option[1:]}" for letter, option in zip(first_letters, options)]
        result = input(f"Enter all stocks to purchase ({display_options}): ").strip().split(' ')
        result_good = [val in first_letters or val in options for val in result]

        good = False

        invalid_message = "Invalid: "

        while not good:
            good = True
            invalid_message = "Invalid: "

            if len(result) > 3:
                invalid_message += "Cannot buy more than 3 stocks. "
                good = False
            if not all(result_good):
                invalid_message += "Invalid stock names/symbols entered. "
                good = False
            if good:
                for i, val in enumerate(result):
                    if val in first_letters: 
                        result[i] = options[first_letters.index(val)]
                for name in stock_names:
                    if result.count(name) > stocks_remaining[name]:
                        invalid_message += f"Cannot buy {result.count(name)} stocks of {name}, only {stocks_remaining[name]} left. "
                        good = False

            if not good:
                print(invalid_message)
                result = input(f"Enter all stocks to purchase ({display_options}): ").strip().split(' ')
                result_good = [val in first_letters or val in options for val in result]

        return result
    
    def get_sell_two_for_one_decision(self, name):
        resp = input(f"Enter: [number of {name} to sell] [number of {name} to 2-for-1]")
        success = False
        
        while not success:
            invalid_message = 'Invalid: '
            success = True
            try:
                try:
                    resp = resp.split(" ")
                    sell = int(resp[0])
                    exchange = int(resp[-1])
                except:
                    invalid_message += 'Input must be two integers.'
                    raise Exception
                
                if exchange % 2 != 0:
                    invalid_message += "Number to 2-for-1 must be even. "
                if (sell + exchange) > self.stocks[name]:
                    invalid_message += "Cannot sell/2-for-1 more than you have"


                assert exchange%2 == 0
                assert (sell + exchange) <= self.stocks[name]
            except:
                success = False
                print("Invalid")
                resp = input(f"Enter: [number to sell] [number to 2-for-1]")

        return resp

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
        


