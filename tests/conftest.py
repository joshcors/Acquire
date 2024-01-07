import pytest

from game import Game
from Game.board import Board
from Game.player import Player

@pytest.fixture
def three_players():
    return [Player("one"), Player("two"), Player("three")]

@pytest.fixture
def four_players(three_players):
    return three_players + [Player("four"), ]

@pytest.fixture
def five_players(four_players):
    return four_players + [Player("five"), ]

@pytest.fixture
def three_player_game(three_players):
    return Game(three_players)

@pytest.fixture
def four_player_game(four_players):
    return Game(four_players)

@pytest.fixture
def five_player_game(five_players):
    return Game(five_players)

@pytest.fixture
def board(four_players):
    return Board(four_players)

@pytest.fixture
def adjacent_safes_board(board, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "Luxor")
    
    for row in ["A", "B"]:
        for col in range(1, 12):
            board.assign(row, str(col))
    
    monkeypatch.setattr('builtins.input', lambda _: "Tower")
    
    for row in ["D", "E"]:
        for col in range(1, 12):
            board.assign(row, str(col))

    return board
