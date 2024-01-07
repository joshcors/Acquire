from Game.player import Player
import json
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

class HotelChain:
    def __init__(self, name, starting_cells):
        self.name = name
        self.cells = starting_cells
        self.safe = False
        self.check_safe()

    def __str__(self) -> str:
        return f"{self.name}: {self.cells}"

    def merge(self, mergee):
        for cell in mergee.cells:
            self.add_cell(cell)

    def add_cell(self, cell):
        if isinstance(cell, tuple):
            cell = cell[0] + cell[1]
        self.cells.append(cell)
        self.check_safe()

    def check_safe(self):
        if not self.safe:
            self.safe = self.size() >= 11

    def size(self):
        return len(self.cells)

class Board:
    ROWS = [letter for letter in "ABCDEFGHI"]
    COLS = [str(number) for number in range(1, 13)]

    def __init__(self, players):
        self.board = {}

        with open(os.path.join(dir_path, "stock_names.txt"), "r") as f:
            self.hotel_names = f.read().splitlines()
        hotels = [HotelChain(name, []) for name in self.hotel_names]
        self.hotels_dict = {name : hotel for name, hotel in zip(self.hotel_names, hotels)}

        self.players = players
        self.dead_cells = []
        self.dead_check_cells = []

        for row in self.ROWS:
            self.board[row] = {}
            for col in self.COLS:
                self.board[row][str(col)] = None
                self.dead_check_cells.append((row, col))

    def __str__(self):
        s = ' ' * 23 + self.COLS[-2] + '\n'
        s += '   ' + ' '.join(self.COLS[:-2]) + '  ' + self.COLS[-1] + '\n'
        s += '  ' + '-' * (12 * 2 + 1)
        s += '\n'

        for row in self.ROWS:
            sub_s = f'{row} |'
            for col in self.COLS:
                h = self.board[row][col]
                if h is None:
                    sub_s += ' |'
                else:
                    sub_s += f'{h[0]}|'
            s += f'{sub_s}\n'

        s += '  ' + '-' * (12 * 2 + 1)
        s += '\n'

        return s

    def available_chains(self):
        available = []
        for chain in self.hotel_names:
            if self.hotels_dict[chain].size() == 0:
                available.append(chain)

        return available

    def get_cell_chain(self, row, col):
        return self.hotels_dict[
            self.board[row][col]
        ]

    @staticmethod
    def surrounding_cells(row, col):
        row_index = Board.ROWS.index(row)
        col_index = Board.COLS.index(col)

        res = []

        for row_adj in [-1, 1]:
            new_row_index = row_index + row_adj
            if new_row_index in [-1, len(Board.ROWS)]:
                continue
            res.append((Board.ROWS[new_row_index], col))

        for col_adj in [-1, 1]:
            new_col_index = col_index + col_adj

            if new_col_index in [-1, len(Board.COLS)]:
                continue

            res.append((row, Board.COLS[new_col_index]))

        return res
    
    def is_single(self, row_col):
        row, col = row_col
        return self.board[row][col] == "Single"
    
    def is_chain(self, row_col):
        row, col = row_col
        return (self.board[row][col] is not None) and (self.board[row][col] != "Single")
    
    def directly_adjacent_single_cells(self, row, col):
        surrounding_cells = self.surrounding_cells(row, col)
        surrounding_singles = list(filter(self.is_single, surrounding_cells))

        return surrounding_singles

    def surrounding_single_cells(self, row, col):
        direct_surrounding_singles = self.directly_adjacent_single_cells(row, col)

        all_surrounding_singles = set()
        all_surrounding_singles.update(direct_surrounding_singles)

        all_surrounding_singles

        _len = len(all_surrounding_singles)
        loop_again = True

        while loop_again:
            loop_again = False
            new_cells = set()

            for cell in all_surrounding_singles:
                new_cells.update(self.directly_adjacent_single_cells(*cell))

            all_surrounding_singles.update(new_cells)

            if _len != len(all_surrounding_singles):
                _len = len(all_surrounding_singles)
                loop_again = True
            

        return all_surrounding_singles
    
    def surrounding_chain_cells(self, row, col):
        surrounding_cells = self.surrounding_cells(row, col)
        surrounding_chains = list(filter(self.is_chain, surrounding_cells))

        return surrounding_chains

    def update_dead_cells(self):
        new_dead_cells = []
        for row, col in self.dead_check_cells:
            surrounding_chain_cells = self.surrounding_chain_cells(row, col)
            surrounding_chains = set([self.board[_row][_col] for _row, _col in surrounding_chain_cells])

            if len(surrounding_chain_cells) < 2:
                continue

            safe_count = 0
            for chain in surrounding_chains:
                safe_count += int(self.hotels_dict[chain].safe)

            if safe_count >= 2:
                new_dead_cells.append((row, col))


        for row, col in new_dead_cells:
                cell = f"{col}{row}"
                self.dead_cells.append(cell)
                self.dead_check_cells.pop(
                    self.dead_check_cells.index((row, col))
                )

    def merge(self, survivor, mergees, additional_cells):
        # Merge all subordinant hotels into survivor and reset them
        for mergee in mergees:
            self.hotels_dict[survivor].merge(
                self.hotels_dict[mergee]
            )

            self.hotels_dict[mergee] = HotelChain(mergee, [])

        # Update board
        for cell in self.hotels_dict[survivor].cells:
            row, col = cell[0], cell[1:]
            self.board[row][col] = survivor

        # Handle adjacent single cells included
        for cell in additional_cells:
            row, col = cell
            self.hotels_dict[survivor].add_cell(cell)
            self.board[row][col] = survivor
    
    def get_new_chain(self, player : Player, options):
        return player.get_new_chain_decision(options)
    
    def get_merger_decision(self, options, player : Player):
        return player.get_merger_decision(options)

    def assign(self, row, col, current_player, initial_draw=False):
        adjacent_cells = self.surrounding_cells(row, col)
        adjacent_hotels = [self.board[_row][_col] for _row, _col in adjacent_cells]
        adjacent_hotels = list(set(filter(lambda x : x is not None, adjacent_hotels)))
        
        if len(adjacent_hotels) == 0:
            hotel = "Single"
            merger = False
        elif len(adjacent_hotels) == 1:
            hotel = adjacent_hotels[0]
            if hotel == "Single" and not initial_draw:
                hotel = self.get_new_chain(current_player, self.available_chains())

                # give 1 free stock
                current_player.buy_stock([hotel, ], [1, ], [0, ])

                additional_cells = self.surrounding_single_cells(row, col)
                mergees = []
                merger = True
            else:
                merger = False

        else:
            merger = True
            additional_cells = self.surrounding_single_cells(row, col)

            if "Single" in adjacent_hotels:
                adjacent_hotels.pop(adjacent_hotels.index("Single"))

            sizes = [self.hotels_dict[name].size() for name in adjacent_hotels]
            max_size = max(sizes)

            if sizes.count(max_size) == 1:
                hotel = adjacent_hotels[sizes.index(max_size)]
            else:
                hotel = self.get_merger_decision(adjacent_hotels, current_player)
            adjacent_hotels.pop(adjacent_hotels.index(hotel))
            mergees = adjacent_hotels

        if hotel != "Single":
            self.hotels_dict[hotel].add_cell(f"{row}{col}")
        self.board[row][col] = hotel

        self.dead_check_cells.pop(self.dead_check_cells.index((str(row), str(col))))
        self.update_dead_cells()

        if merger:
            self.merge(hotel, mergees, additional_cells)
            return {"survivor": hotel, "mergees": mergees}
        else:
            return None

if __name__=="__main__":
    players = [Player("None") for i in range(4)]
    board = Board(players)

    board.assign("A", "1")
    print(board)
    board.assign("A", "2", initial_draw=True)
    print(board)
    board.assign("B", "1", initial_draw=True)
    print(board)
    board.assign("B", "2", initial_draw=True)
    print(board)
    board.assign("B", "3")
    print(board)
    board.assign("C", "10")
    print(board)
    board.assign("C", "9")
    print(board)
    board.assign("C", "8")
    print(board)

    board.assign("E", "11")
    print(board)
    board.assign("E", "10")
    print(board)
    board.assign("E", "9")
    print(board)
    board.assign("E", "8")
    print(board)

    board.assign("D", "6")
    print(board)
    board.assign("D", "7")
    print(board)

    board.assign("D", "8")
    print(board)

    print(board)

    for name in board.hotels_dict:
        print(board.hotels_dict[name])