import pytest
import random

from Game.player import Player
from game import Game

random.seed(1234)

class TestPlayer:
    def test_tile_selection(self, monkeypatch, three_player_game):
        index = three_player_game.current_player_index

        # creating iterator object
        answers = list(three_player_game.players[index].tiles)

        for tile in answers:

            monkeypatch.setattr('builtins.input', lambda _: tile)
            selected_tile = three_player_game.players[index].get_tile_selection()
            
            assert tile == selected_tile

    def test_bad_then_good_tile_selection(self, monkeypatch, three_player_game):
        index = three_player_game.current_player_index

        # Bad input followed by good input
        correct_answer = three_player_game.players[index].tiles[0]
        answers = [correct_answer + "badtile1", correct_answer + "badtile2", correct_answer]
        answers = iter(answers)

        monkeypatch.setattr("builtins.input", lambda _: next(answers))

        selected_tile = three_player_game.players[index].get_tile_selection()
        
        assert selected_tile == correct_answer