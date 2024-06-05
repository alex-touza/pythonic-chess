from os.path import isfile
from typing import overload

import board
from board import *
from forms import Opcio, clear, title, pausar
from menu import Menu
from random import choice

BOUNDS = Bounds(0, 0, 8, 8)


def gameHelp():
	print("Entrada:")
	Colors.cian()
	print("\tun moviment en notació algebraica (e.g. 'Pa1a2', 'b3', 'Th6')")
	print(f"\t{Estils.cursiva('?[cel·la]')} per veure moviments possibles d'una peça (e.g. '?a1')")
	print(f"\t{Estils.cursiva('$')} per fer un moviment aleatori")
	print(f"\t{Estils.cursiva('exit')} per aturar el joc")
	print(f"\t{Estils.cursiva('h')} o {Estils.cursiva('help')} per mostrar aquesta ajuda")
	Colors.reset()


class Game:
	def __init__(self):
		self.turn = Team.WHITE
		self.pieces = Board.init()
		self.board = thisBoard
		self.history: list[tuple[Team, Move]] = []

	def __call__(self) -> bool:
		clear()

		self.show()

		res = ""

		while True:
			# look for check

			king = self.turn.get(PieceKind.KING)[0]
			
			q = Move.query(str(king.cell), self.turn.opponent)
			self.turn.in_check = q is not None and len(q) > 0
	

			# look for checkmate
			if q is not None and len(q) == 2:
				can_escape = False
				for c in king.get_moves():
					if isinstance(c, Board.Cell):
						q = Move.query(str(c), self.turn.opponent)
						if len(q) == 0:
							can_escape = True
							break
				
					
				
			# 1. can the threatening piece be captured?


			res = input(Colors.groc_fosc)
			Colors.reset()
			
			if res == '':
				continue
				
			if res == 'h' or res == 'help':
				gameHelp()
			elif res == 'exit':  # ctrl-d
				i = 1
				while isfile(f"joc{i}.pych"):
					i += 1
					
				print("Desant partida...")
				
				try:
					with open(f"joc{i}.pych", "w") as f:
						for m in self.history:
							f.write(str(m[1]) + '\n')

				except Exception as e:
					print(Colors.vermell("Hi ha hagut un error"))
					print(e)
					print()
				else:
					print(Colors.verd(f"S'ha desat el fitxer com a joc{i}.pych."))
					
				pausar()
				return False
			elif res == '$':
				moves = []
				
				for k in PieceKind:
					for p in self.turn.get(k):
						if p.cell:
							moves.extend([Move(p, p.cell, c) for c in p.get_moves() if isinstance(c, Board.Cell)])
				
				move = choice(moves)
				assert move is not None
				move()
				self.history.append((self.turn, move))
				self.turn = Team.BLACK if self.turn == Team.WHITE else Team.WHITE
				clear()

				self.show()
				
				
				
			elif len(res) > 0 and res[0] == '?':

				moves = None
				try:
					cell = self.board[res[1:]]
					assert cell.piece
					moves = Move.get_moves(cell.piece)
				except:
					print(Colors.vermell("Error en cercar els moviments."))
					continue
				clear()
				self.show([m.dest for m in moves])

				if len(moves) > 0:
					print(Colors.cian("Moviments possibles des de ") + res[1:] + Colors.cian(':'))
					for m in moves:
						print(f'\t{m}')
				else:
					print(Colors.groc("Cap moviment possible des de ") + res[1:])

			else:
				move = None
				try:
					move = Move.from_notation(res, self.turn)
				except SyntaxError:
					print(Colors.vermell("Sintaxi invàlida"))
				except TypeError:
					print(Colors.vermell("Entrada invàlida"))
				except Move.NotationBaseError as e:
					if isinstance(e, Move.AmbiguousMoveError):
						print(Colors.groc("Moviment ambigu"))
						for m in e.moves:
							print(f'\t{m}')
					else:
						print(Colors.vermell("Moviment invàlid"))
						print(Colors.vermell(e.message))
				else:
					assert move is not None
					move()
					self.history.append((self.turn, move))
					self.turn = Team.BLACK if self.turn == Team.WHITE else Team.WHITE
					clear()

					self.show()

	def show(self, highlight: list[Board.Cell] | None = None, _title="Joc d'escacs"):
		title(_title)
		print(Estils.subratllat(Estils.negreta(self.turn.locale)) + ' ' + (
			"Escac i mat" if Team.WHITE.in_check or Team.BLACK.in_check else ""))

		print(Board.render(highlight))
