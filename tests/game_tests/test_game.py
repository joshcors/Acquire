import pytest
import random

random.seed(1234)
import time
class TestGame:
    def test_game(self, monkeypatch, three_player_game):
        for i in range(10):
            tile = three_player_game.current_player.tiles[0]

            answers = iter([tile, "L", "L L L"])

            monkeypatch.setattr("builtins.input", lambda _: next(answers))
            three_player_game.turn()