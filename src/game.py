from Game.board import Board
from Game.player import Player
from Game.stock import Stock

import os
from itertools import product

from random import randint

dir_path = os.path.dirname(os.path.realpath(__file__))

class Game:
    def __init__(self, player_names):
        self.players = [Player(name) for name in player_names]
        self.current_player_index = 0

        with open(os.path.join(dir_path, "Game", "stock_names.txt"), 'r') as f:
            self.stock_names = f.read().splitlines()

        self.stocks = {name : Stock(name) for name in self.stock_names}
        self.stocks_remaining = {name : 25 for name in self.stock_names}
        self.hotel_in_play = {name : False for name in self.stock_names}

        self.board = Board(self.players)

        self.tiles = [''.join(col_row) for col_row in product(Board.COLS, Board.ROWS)]

        self.initialize_board()
        self.initialize_players()

    def get_row_col_from_tile(self, tile):
        """Extract row and column tuple from tile string"""
        return tile[-1], tile[:-1]

    def get_random_tile(self):
        """Get random tile from remaining tiles"""
        ind = randint(0, len(self.tiles) - 1)
        tile = self.tiles.pop(ind)

        return tile
    
    def get_valid_random_tile(self):
        """Get random tile from remaining tiles, weeding out now-dead cells"""
        tile = self.get_random_tile()
        while tile in self.board.dead_cells:
            tile = self.get_random_tile()

        return tile

    def initialize_board(self):
        """Initialize board with initial drawn tiles"""
        self.initial_tiles = []
        for i in range(len(self.players)):
            self.initial_tiles.append(
                self.get_random_tile()
            )

        _min = 10_000
        min_ind = -1

        for i, tile in enumerate(self.initial_tiles):
            val = Board.COLS.index(tile[:-1]) * 100 + Board.ROWS.index(tile[-1])
            if val < _min:
                _min = val
                min_ind = i
        
        self.current_player_index = min_ind

        for tile in self.initial_tiles:
            self.board.assign(*self.get_row_col_from_tile(tile), initial_draw=True)
    
    def initialize_players(self):
        """Draw initial tiles for each player"""
        for i in range(6):
            for j in range(len(self.players)):
                self.players[j].add_tile(self.get_valid_random_tile())

    def turn(self):
        """
        Take turn of current player, consisting of:
        1. Placing tile
        2. Handling merger sale/2-for-1
        3. Handle stock purchase
        """
        print(self.board)
        self.board.set_current_player(self.current_player_index)
        tile = self.players[self.current_player_index].get_tile_selection()

        merger_results = self.board.assign(*self.get_row_col_from_tile(tile))

        for name in self.stock_names:
            size = self.board.hotels_dict[name].size()
            if size >= 2:
                self.stocks[name].set_current_info(size)
            self.hotel_in_play[name] = size >= 2

        # Handle sales and 2-for-1
        if merger_results is not None:
            self.handle_sale_and_two_for_one(merger_results)

        for tile in self.players[self.current_player_index].tiles:
            if tile in self.board.dead_cells:
                new_tile = self.get_valid_random_tile()

                print(f"Current player's tile {tile} now dead, replacing")
                self.players[self.current_player_index].replace_tile(tile, new_tile)

        new_tile = self.get_valid_random_tile()
        self.players[self.current_player_index].add_tile(new_tile)

        if any(self.hotel_in_play.values()):
            options = []
            for name in self.hotel_in_play:
                if self.hotel_in_play[name]:
                    options.append(name)

            purchases = self.players[self.current_player_index].get_buy_selections(options)
            good_purchases = False
            while not good_purchases:
                good_purchases = True
                for name in self.stock_names:
                    if purchases.count(name) > self.stocks_remaining[name]:
                        print(f"Cannot buy {purchases.count(name)} stocks of {name}, only {self.stocks_remaining[name]} left")
                        good_purchases = False

            purchase_names = list(set(purchases))
            counts = [purchases.count(name) for name in purchase_names]
            prices = [self.stocks[name].current_price for name in purchase_names]

            self.players[self.current_player_index].buy_stock(purchase_names, counts, prices)

        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def handle_sale_and_two_for_one(self, merger_results):
        """From merger results, allow player to sell, 2-for-1, or keep"""
        survivor = merger_results['survivor']
        mergees = merger_results['mergees']

        for name in mergees:
            if self.players[self.current_player_index].stocks[name] == 0:
                continue

            number_held = self.players[self.current_player_index].stocks[name]

            print(f"You own {number_held} of {name}, which has just been absorbed by {survivor}")
            print(f"{name} is worth ${self.stocks[name].current_price}")
            print(f"{survivor} is worth ${self.stocks[name].current_price}")
            resp = input(f"Enter: [number to sell] [number to 2-for-1]")
            success = False
            while not success:
                success = True
                try:
                    resp = resp.split(" ")
                    sell = int(resp[0])
                    exchange = int(resp[-1])
                    assert exchange%2 == 0

                    self.handle_sale([name, ], [sell, ])
                    self.handle_two_for_one(name, survivor, exchange)
                except:
                    success = False
                    print("Invalid")
                    resp = input(f"Enter: [number to sell] [number to 2-for-1]")

    def handle_sale(self, names, counts):
        """Pass stock sale info to player"""
        self.players[self.current_player_index].sell_stock(names, counts, [self.stocks[name].current_price for name in names])

    def handle_two_for_one(self, old_name, new_name, number):
        """Pass 2-for-1 info to player"""
        self.players[self.current_player_index].two_for_one(old_name, new_name, number)

