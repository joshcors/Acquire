from Game.board import Board
from Game.player import Player
from Game.stock import Stock

import os
from itertools import product
from math import ceil

from random import randint

dir_path = os.path.dirname(os.path.realpath(__file__))

class Game:
    def __init__(self, players):
        self.players = players
        for i in range(len(players)):
            if isinstance(self.players[i], str):
                self.players[i] = Player(self.players[i])

        self.player_names = [player.name for player in self.players]
        self.player_dict = {player.name : player for player in self.players}
        self.current_player_index = 0

        with open(os.path.join(dir_path, "stock_names.txt"), 'r') as f:
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
        self.current_player = self.players[self.current_player_index]

        for i, tile in enumerate(self.initial_tiles):
            self.board.assign(*self.get_row_col_from_tile(tile), self.players[i], initial_draw=True)
    
    def initialize_players(self):
        """Draw initial tiles for each player"""
        for i in range(6):
            for j in range(len(self.players)):
                self.players[j].add_tile(self.get_valid_random_tile())

    def turn_tile_stage(self, tile_selected):
        self.current_player = self.players[self.current_player_index]

        success = self.current_player.handle_tile_selection(tile_selected)

        print(f"Tile {tile_selected} {'not ' * (not success)}successfully added")

        return success

    def turn(self):
        """
        Take turn of current player, consisting of:
        1. Placing tile
        2. Handling merger sale/2-for-1
        3. Handle stock purchase
        """
        self.current_player = self.players[self.current_player_index]
        
        tile = self.players[self.current_player_index].get_tile_selection()

        merger_results = self.board.assign(*self.get_row_col_from_tile(tile), self.players[self.current_player_index])

        for name in self.stock_names:
            size = self.board.hotels_dict[name].size()
            if size >= 2:
                self.stocks[name].set_current_info(size)
            self.hotel_in_play[name] = size >= 2

        # Handle sales and 2-for-1
        if merger_results is not None:
            self.stocks_remaining[merger_results["survivor"]] -= 1
            self.handle_merger_bonuses(merger_results["mergees"])
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

            purchases = self.players[self.current_player_index].get_buy_selections(options, self.stock_names, self.stocks_remaining)

            purchase_names = list(set(purchases))
            counts = [purchases.count(name) for name in purchase_names]
            prices = [self.stocks[name].current_price for name in purchase_names]

            for name, count in zip(purchase_names, counts):
                self.stocks_remaining[name] -= count

            self.players[self.current_player_index].buy_stock(purchase_names, counts, prices)

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]

    def handle_merger_bonuses(self, mergees):
        for mergee in mergees:
            first_place_bonus = self.stocks[mergee].current_bonus
            second_place_bonus = first_place_bonus // 2

            first_number = 0
            first_player_index = []

            second_number = 0
            second_player_index = []

            for i in range(len(self.players)):
                n = self.players[i].stocks[mergee]
                if n > first_number:
                    second_number = first_number
                    second_player_index = first_player_index

                    first_number = n
                    first_player_index = [i, ]

                elif n == first_number:
                    first_player_index.append(i)

                elif n > second_number:
                    second_number = n
                    second_player_index = [i, ]
                
                elif n == second_number:
                    second_player_index.append(i)

            if len(first_player_index) > 1:
                bonus = (first_place_bonus + second_place_bonus) / len(first_player_index)
                # Round up to nearest hundred
                bonus = ceil(bonus / 100) * 100

                for index in first_player_index:
                    self.players[index].money += bonus

                continue
            if len(first_player_index) == 0:
                raise Exception("Something's hinky")

            self.players[first_player_index[0]].money += first_place_bonus

            second_place_bonus = second_place_bonus / len(second_player_index)
            second_place_bonus = ceil(second_place_bonus / 100) * 100

            for index in second_player_index:
                self.players[index].money += second_place_bonus

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
            resp = self.players[self.current_player_index].get_sell_two_for_one_decision(name)
            sell = int(resp[0])
            exchange = int(resp[-1])

            self.handle_sale([name, ], [sell, ])
            self.handle_two_for_one(name, survivor, exchange)

    def handle_sale(self, names, counts):
        """Pass stock sale info to player"""
        self.players[self.current_player_index].sell_stock(names, counts, [self.stocks[name].current_price for name in names])

    def handle_two_for_one(self, old_name, new_name, number):
        """Pass 2-for-1 info to player"""
        self.players[self.current_player_index].two_for_one(old_name, new_name, number)

