from enum import Enum
from os.path import isfile
from typing import Sequence, reveal_type

from colorama import init
from colorama.ansi import set_title

from board import *
from game import Game, gameHelp
from lib.forms import pausar, clear
from lib.menu import Menu
from lib.text import Colors, Estils
from plane import Bounds, Direction


class GameMenu(Menu):
	def __init__(self):
		pieces = [PieceKind.QUEEN, PieceKind.KNIGHT]

		icons = [Estils.reset(' '.join([p.icon[t] for p in (pieces if t is Team.WHITE else pieces[::-1])])) for t in
		         Team]

		super().__init__(icons[0] + '  ' + Estils.negreta("PythonicChess") + ' ' + icons[1] + '  ')

	@Menu.menu(descr="Benvingut al joc d'escacs pitònic.")
	def __call__(self):
		pass

	@Menu.tool("Nou joc", 1)
	def start(self):
		gameHelp()

		print(Colors.verd("Prem enter per començar la partida!"))
		print()
		input()

		game = Game()

		while game(): pass

	@Menu.tool("Veure jocs desats", 2)
	def saved(self):
		p: str | None = None

		while not p:
			p = input("Introdueix un fitxer de partida: ")
			if p == "": return

			if not isfile(p):
				print(Colors.vermell("El fitxer no existeix."))
				p = None

			if p is not None and not p.endswith(".pych"):
				print(Colors.vermell("El fitxer no té l'extensió correcta."))

		game = Game()
		clear()
		with open(p, "r") as f:
			for line in f:
				print("Prem enter per veure el següent torn")
				input()
				m = Move.from_notation(line.strip(), game.turn)
				game.turn = Team.WHITE if game.turn is Team.BLACK else Team.BLACK

				m()

				game.show(_title=p)



		print(Colors.blau("El joc ha acabat."))
		input()




"""menu = GameMenu()

while menu():
	pass


def f(l: Sequence[int | str]):
	print(isinstance(l, Sequence))


f(["a", 1])

bounds = Bounds(0, 0, 8, 8)

Board.init(bounds)

thisBoard["a1"].piece.place(thisBoard["d5"])

p = thisBoard["a2"].piece
assert p
c = p.get_moves()[1]
assert isinstance(c, Board.Cell)
move = Move.from_coords(p, c.obj)
print(move)
print(thisBoard)
move()
print(thisBoard)
print(thisBoard["g8"].piece.get_moves())

"""