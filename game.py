from typing import overload

from board import Piece, Board, Coords


class Move:
	@overload
	def __init__(self, piece: Piece, dest: Board.Cell):
		pass

	@overload
	def __init__(self, board: Board, s: str):
		pass

	def __init__(self, a: Piece | Board, b: Board.Cell | str):
		if isinstance(a, Piece):
			assert isinstance(b, Board.Cell)
			self.piece = a
			self.dest = b
		else:
			assert isinstance(a, Board) and isinstance(b, str)

			if not 2 <= len(b) <= 5:
				raise ValueError

			self.dest = a[b[-2:]]

