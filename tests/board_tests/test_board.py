import pytest

class TestBoard:
    def test_dead_cells(self, adjacent_safes_board):
        print(adjacent_safes_board.dead_cells)
        for col in range(1, 12):
            assert f"{col}C" in adjacent_safes_board.dead_cells