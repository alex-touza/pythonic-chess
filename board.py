# pyright: reportIncompatibleMethodOverride=false

from __future__ import annotations
from typing_extensions import reveal_type

from plane import CardinalDirection, FreeVector, Point, Ref, Bounds, Vector, Unit, FixedVector, Direction
from enum import Enum
from typing import Mapping, Sequence, overload, Type, TypeVar, Callable, TYPE_CHECKING, Literal, NoReturn
from abc import ABC, abstractmethod

class RelativeFreeVector(FreeVector):
	@overload
	def __init__(self, dx: int, dy: int):
		pass

	@overload
	def __init__(self, d: CardinalDirection):
		pass

	def __init__(self, a: int | CardinalDirection, b: int | None = None):
		if b is None:
			assert isinstance(a, CardinalDirection)
			RelativeFreeVector(a.dx, a.dy)
		else:
			assert isinstance(a, int)
			super().__init__(a, b)
			self.dx = a
			self.dy = b

	def mirrored(self):
		return RelativeFreeVector(-self.dx, -self.dy)


class Move(FixedVector):
	def __init__(self, piece: Piece, origin: Board.Cell, dest: Board.Cell, capture: Piece | None):
		self.piece = piece
		self.origin = origin
		self.dest = dest
		self.capture = capture

		super().__init__(self.origin.obj.x, self.origin.obj.y, self.dest.obj.x, self.dest.obj.y, self.origin, self.dest)

	@staticmethod
	def from_notation(s: str) -> Move:
		"""
		Returns the Move object described by the provided string. The string must use algebraic notation and may use
		shortened versions. It is recommended to always provide the full form, since ambiguous moves will raise an error.

		If the piece kind is omitted, it is assumed that the move refers to the piece with the lowest score (in the case
		of traditional chess, the pawn).

		Capture symbol 'x' may always be omitted, but an error will be raised if it is included and the move does not
		actually capture a piece.

		Minimal algebraic notation, however, is not allowed; hence, the provided string must have a minimum length of 2.

		>>> Move.from_notation('a1', board), Move.from_notation('R1a3'), Move.from_notation('Bxe5')

		@raise TypeError if the provided object is not a string, its length is not appropriate, or it's not properly formatted.
		@raise ArithmeticError if the move is illegal or would send the piece outside the board.
		@raise ValueError if the move does not capture a piece and the capture symbol was specified.
		@raise LookupError if the move is ambiguous, there is no piece that can be moved to the provided destination position
		or there is no piece in the provided origin position.
		@raise NameError if the provided piece kind does not exist.
		"""
		if not (isinstance(s, str) and 2 <= len(s) <= 5):
			raise TypeError

		if not len(s) == 4:
			raise NotImplementedError

		origin = board[s[:3]]
		dest = board[s[-2:]]

		if origin is None or dest is None:
			raise ArithmeticError

		if origin.piece is None:
			raise LookupError

		return Move(origin.piece, origin, dest, None)

	@staticmethod
	def from_vector(piece: Piece, v: RelativeFreeVector):
		pass

	def __str__(self):
		return f"{self.piece.kind.short}{self.origin}{'x' if self.capture is not None else ''}{self.dest}"


class Letter(Enum):
	a = 0
	b = 1
	c = 2
	d = 3
	e = 4
	f = 5
	g = 6
	h = 7


class Piece:


	def __init__(self, team: Team, kind: PieceKind, cell: Board.Cell):
		self.team = team
		self.kind = kind
		self.cell: Board.Cell | None = cell
		self.place(cell)
		self.history: list[Move] = []

	def place(self, cell: Board.Cell):
		if self.cell:
			self.cell.piece = None
		self.cell = cell
		cell.piece = self

	def move(self, move: Move):
		assert move.origin is self.cell and move.piece is self

		self.place(move.dest)
		self.history.append(move)

	def is_move_possible(self, v: RelativeFreeVector, captures: bool | None = None) -> Board.Cell | None:
		assert self.cell is not None
		
		coord = self.cell.get(v)
		cell = Board.get_cell(coord)
		is_within = Board.bounds.is_within(coord)

		if not cell or not is_within: return None
			
		if captures: # must capture
			return cell if cell.piece and cell.piece.team != self.team else None
		elif captures is None: # may capture
			return None if cell.piece and cell.piece.team == self.team else None
	
		
		return c if Board.bounds.is_within(coord) and (lambda )((c := Board.get_cell(coord)).piece and c.piece.team != self.team) else None



	def get(self, v: RelativeFreeVector):
		pass

	def get_moves(self) -> list[Coords]:
		assert self.cell
		
		destinations: list[Coords] = []
		
		for m in self.kind.get_moves(self.team):
			if isinstance(m, CardinalDirection):
				destinations.extend(Board.get_points(self.cell.obj, m, self.team))
			
			else:
				c = Board.get_cell(self.cell.obj + m)
				if c is not None and Board.bounds.is_within(c.obj) and (not c.piece or c.piece.team != self.team):
					destinations.append(c.obj)

		destinations.extend([reveal_type(k) for k, v in self.kind.special(self).items()])

		print([reveal_type(k) for k, v in self.kind.special(self).items()])
				
		return destinations
				


class Team(Enum):
	WHITE = 'Y'
	BLACK = ('Z', True)

	def __init__(self, id: str, mirrored=False) -> None:
		self.id = id
		self.mirrored = mirrored
		super().__init__()

	@property
	def opponent(self) -> Team:
		if self is Team.WHITE:
			return Team.BLACK
		else:
			return Team.WHITE

	def __invert__(self) -> Team:
		return self.opponent


class Coords(Point):
	@overload
	def __init__(self, c: str):
		pass

	@overload
	def __init__(self, x: Letter, y: int):
		pass

	@overload
	def __init__(self, p: Point):
		pass

	@overload
	def __init__(self, x: int, y: int):
		pass

	def __init__(self, a: Point | Letter | int | str, b: int | None = None):
		if isinstance(a, Point):
			super().__init__(a.x, a.y)

		elif isinstance(a, Letter):
			assert isinstance(b, int)

			super().__init__(a.value, b)

		elif isinstance(a, int):
			assert b is not None
			super().__init__(a, b)

		else:
			self.__init__(Letter[a[0].lower()], int(a[1]) - 1)

	@property
	def file(self):
		return Letter(self.x)

	@property
	def rank(self):
		return self.y + 1

	def invert(self) -> Coords:
		return Board.get_cell(Board.bounds.get_mirrored_point(self, Direction.VERTICAL)).obj

	

	def __str__(self):
		return str(self.file.name) + str(self.rank)


	def __add__(self, other: tuple[int, int] | Vector) -> Coords:
		return Coords(super().__add__(other))

class PieceKindOptions:
	def __init__(self, jumping: bool=False,) -> None:
 		self.jumping = jumping
		
class SpecialMovesList:
	def __init__(self, dests: list[Board.Cell | tuple[str, Callable[..., Board.Cell]]], override: bool=False):
		self.dests = dests
		self.override = override



def special_pawn(piece: Piece) -> Mapping[Board.Cell | RelativeFreeVector, None]:
	assert piece.cell is not None

	moves: list[Board.Cell | RelativeFreeVector] = []
	if len(piece.history) == 0:
		coord = piece.cell.get(RelativeFreeVector(0, 2))
		moves.append(RelativeFreeVector(0, 2))
		if Board.bounds.is_within(coord) and (c := Board.get_cell(coord)).piece and c.piece.team != piece.team:
			

	
	for v in [RelativeFreeVector(1, 1), RelativeFreeVector(-1, 1)]:
		coord = piece.cell.get(v)
		if Board.bounds.is_within(coord) and (c := Board.get_cell(coord)).piece and c.piece.team != piece.team:
			moves.append(c)


	return {m: None for m in moves}

# TODO: Metaclasses?
class PieceKind(Enum):
		
	PAWN = ("peó", 'P', 1, ('♟', '♙'), ["a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2"], [FreeVector(0, 1)], special_pawn)
	KNIGHT = ("cavall", 'C', 3, ('♞', '♘'), ["b1", "g1"], CardinalDirection.get_rotations(1, 2), None, PieceKindOptions(jumping=True))
	BISHOP = ("alfil", 'A', 5, ('♝', '♗'), ["c1", "f1"], CardinalDirection.D_CROSS())
	ROOK = ("torre", 'T', 5, ('♜', '♖'), ["a1", "h1"], CardinalDirection.CROSS())
	QUEEN = ("reina", 'D', 9, ('♛', '♕'), "d1", CardinalDirection.ALL())
	KING = ("rei", 'R', 10, ('♚', '♔'), "e1", [*CardinalDirection.get_rotations(1, 0), *CardinalDirection.get_rotations(1, 1)])

	def __init__(self, name: str, short: str, values: int, icon: tuple[str, str],
	             initial_pos: Coords | str | Sequence[Coords | str],
	             moves: Sequence[FreeVector | CardinalDirection],
	             special: Callable[[Piece], Mapping[Board.Cell | RelativeFreeVector, None]] | Callable[[Piece], Mapping[str, Callable]] | None= None, options = PieceKindOptions()
	             ) -> None:
		self._name = name
		self.short = short
		self.values = values
		self.icon = {Team.WHITE: icon[0], Team.BLACK: icon[1]}
		self.initial_pos = [(p if isinstance(p, Coords) else Coords(p))
		                    for p in ([initial_pos] if isinstance(initial_pos, str) or isinstance(initial_pos, Coords) else initial_pos)]
		self.moves = [m if isinstance(m, CardinalDirection) else RelativeFreeVector(m.dx, m.dy) for m in moves]
		self.special = special
		self.options = options
		

	def __call__(self) -> list[Piece]:
		return [Piece(Team.WHITE, self, Board.get_cell(p)) for p in self.initial_pos] + [Piece(Team.BLACK, self, Board.get_cell(Board.bounds.get_mirrored_point(p, Direction.VERTICAL))) for p in self.initial_pos]

	def get_moves(self, team: Team) -> Sequence[FreeVector | CardinalDirection]:
		return [m.mirrored() for m in self.moves] if team.mirrored else self.moves


	@staticmethod
	def from_letter(s: str):
		l = [p for p in PieceKind if p.short == s]

		return l[0] if len(l) else None

				
			
			
		


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
	class Cell(Ref[Coords]):
		def __init__(self, pos: Point):
			self.piece: Piece | None = None

			c = Coords(pos)
			super().__init__(str(c), c)

		def __bool__(self):
			return bool(self.piece)

		def place(self, piece: Piece):
			if self.piece:
				self.piece.cell = None
				self.piece = None
			self.piece = piece
			piece.cell = self

	
			

		def get(self, d: RelativeFreeVector) -> Coords:
			v: FreeVector = d.mirrored() if (self.piece and self.piece.team.mirrored) else d

			return self.obj + v

		def invert(self) -> Board.Cell:
			return Board.get_cell(Board.bounds.get_mirrored_point(self.obj, Direction.VERTICAL))

		def __add__(self, d: RelativeFreeVector):
			return self.get(d)

		def __str__(self):
			return self.obj.__str__()

	matrix: list[list[Cell]]
	bounds: Bounds
	
	@classmethod
	def get_points(cls, origin: Coords, v: CardinalDirection, team: Team) -> list[Coords]:
		l = []
		i = 1
		while True:
			try:
				d = (origin + v.vector * i)
				if cls.bounds.is_within(d):
					break

				c = cls.get_cell(d)

				if c.piece and c.piece.team == team:
					break
			except:
				c = None

			i += 1

			if c is None: break

			l.append(c)

			if c.piece is not None:
				break

		return l

	@classmethod
	def init(cls, bounds: Bounds) -> None:
		cls.matrix: list[list[Board.Cell]] = [[Board.Cell(Point(j, i)) for j in range(bounds.width)] for i in range(bounds.height)]
		cls.bounds = bounds
		
		for kind in PieceKind:
			kind()
		

	@classmethod
	@overload
	def get_cell(cls, x: int, y: int) -> Board.Cell:
		pass

	@classmethod
	@overload
	def get_cell(cls, p: Point | str) -> Board.Cell:
		pass

	@classmethod
	@overload
	def get_cell(cls, o: Cell, d: RelativeFreeVector) -> Board.Cell:
		pass

	@classmethod
	def get_cell(cls, a: Cell | Point | str | int, b: RelativeFreeVector | int | None = None) -> Board.Cell:
		if isinstance(a, Board.Cell):
			assert isinstance(b, RelativeFreeVector)
			return cls.get_cell(a.get(b))
			
		if isinstance(a, int):
			assert isinstance(b, int)
			assert cls.bounds.is_within(Point(a, b))
			return cls.matrix[b][a]
	

		if isinstance(a, str):
			a = Coords(a)

		assert isinstance(a, Point)

		assert cls.bounds.is_within(a)

		return cls.get_cell(a.x, a.y)
		

	@classmethod
	def is_move_possible(cls, origin: Cell, d: RelativeFreeVector):
		assert origin.piece
		c = cls.get_cell(origin, d)
		return c is not None and cls.bounds.is_within(c.obj) and (not c.piece or c.piece.team != origin.piece.team)

	
	def __class_getitem__(cls, c: str) -> Board.Cell | None:
		return cls.get_cell(c)

	@classmethod
	def render(cls):
		s = "  "

		for i in range(cls.bounds.width):
			s += Letter(i).name + " "

		s += '\n'
		i = cls.bounds.height
		
		for row in cls.matrix[::-1]:
			s += str(i) + " "
			
			for p in row:
				s += (p.piece.kind.icon[p.piece.team] if p.piece else " ") + " "

				
			i -= 1
			s += '\n'

			

		return s

class BoardAlias:
	def __getitem__(self, c: str) -> Board.Cell:
		return Board.get_cell(c)

	def __call__(self) -> type[Board]:
		return Board

	def __str__(self):
		return Board.render()

	

board = BoardAlias()