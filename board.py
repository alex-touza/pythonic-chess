from __future__ import annotations

from plane import Plane, Directions, FreeVector, Point, Ref, Bounds, Vector
from enum import Enum
from typing import Sequence, overload, Type, TypeVar, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod


class Team(Enum):
	WHITE = 'Y'
	BLACK = 'Z'


class PieceKind(Enum):
	PAWN = ("peó", 'P', 1, ('♟', '♙'), [FreeVector(0, 1)], [FreeVector(1, 1), FreeVector(-1, 1)])
	KNIGHT = ("cavall", 'C', 3, ('♞', '♘'), Directions.get_rotations(1, 2))
	BISHOP = ("alfil", 'A', 5, ('♝', '♗'), Directions.D_CROSS())
	ROOK = ("torre", 'T', 5, ('♜', '♖'), Directions.CROSS())
	QUEEN = ("reina", 'D', 9, ('♛', '♕'), Directions.ALL())
	KING = ("rei", 'R', 10, ('♚', '♔'), [*Directions.get_rotations(1, 0), *Directions.get_rotations(1, 1)])

	def __init__(self, name: str, short: str, values: int, icon: tuple[str, str],
	             moves: Sequence[FreeVector | Directions], get_places: Callable[[Board, PieceKind,], str]
	             ) -> None:
		self._name = name
		self.short = short
		self.values = values
		self.moves = moves
		self.icon = icon
		super().__init__()


class Letters(Enum):
	a = 1
	b = 2
	c = 3
	d = 4
	e = 5
	f = 6
	g = 7
	h = 8


class Coords(Point):
	@overload
	def __init__(self, c: str):
		pass

	@overload
	def __init__(self, x: Letters, y: int):
		pass

	@overload
	def __init__(self, p: Point):
		pass

	@overload
	def __init__(self, x: int, y: int):
		pass

	def __init__(self, a: Point | Letters | int | str, b: int = None):
		if isinstance(a, Point):
			super().__init__(a.x, a.y)

		elif isinstance(a, Letters):
			assert isinstance(a.value, int)

			super().__init__(a.value, b)

		elif isinstance(a, int):
			super().__init__(a, b)

		else:
			self.__init__(Letters[a[0]], int(a[1]))

	@property
	def file(self):
		return Letters(self.x)

	@property
	def rank(self):
		return self.y

	def __str__(self):
		return str(self.file.name) + str(self.rank)

	def __add__(self, other: tuple[int, int] | Vector) -> Coords:
		return Coords(super().__add__(other))

class Piece:
	def __init__(self, team: Team, kind: PieceKind, cell: Board.Cell):


# class Piece(Cell):
# 	def __init__(self, board: Board, team: Team, kind: PieceKind, pos: str):
# 		self.team = team
# 		self.kind = kind
#
# 		super().__init__(board, pos)
#
# 	def move(self, vector: FreeVector) -> bool:
# 		pass
#
#	def possible_moves(self) -> Sequence[FreeVector]:
#		r: list[Point] = []
#
#		if self.kind.attack:
#			for m in self.kind.attack:
#				cf = self.board.get_cell(self + m)
#
#				if cf:
#
#		for l in self.kind.moves:


class Board:
	class Cell(Coords):
		def __init__(self, board: Board, pos: Point):
			self.board = board
			self.piece: Piece | None = None

			super().__init__(pos)

		def __bool__(self):
			return bool(self.piece)

	@staticmethod
	def get_points(origin: Coords, v: FreeVector | Directions) -> list[Coords]:
		if isinstance(v, FreeVector):
			return [origin + v]
		else:
			l = []

	def __init__(self, bounds: Bounds) -> None:
		self.matrix: list[list[Board.Cell]] = [[Board.Cell(self, Point(j, i)) for j in range(bounds.width)] for i in
		                                       range(bounds.height)]
		self.bounds = bounds

	@overload
	def get_cell(self, x: int, y: int) -> Board.Cell:
		pass

	@overload
	def get_cell(self, c: Point | str):
		pass

	def get_cell(self, a: Point | str | int, b: int | None = None) -> Board.Cell:
		if isinstance(a, int):
			return self.matrix[a][b]

		if isinstance(a, str):
			a = Coords(a)

		assert isinstance(a, Coords)

		return self.matrix[a.y][a.x]

	def __getitem__(self, c: str):
		return self.get_cell(c)
