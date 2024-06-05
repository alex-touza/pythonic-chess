# pyright: reportIncompatibleMethodOverride=false

from __future__ import annotations

from dataclasses import dataclass, asdict

from lib.text import Estils, Colors

from plane import CardinalDirection, FreeVector, Point, Ref, Bounds, Vector, FixedVector, Direction
from enum import Enum
from typing import Mapping, Sequence, overload, TypeVar, Callable

T = TypeVar('T')


def might_eq(a: T | None, b: T) -> bool:
	return a is None or a == b


class RelativeFreeVector(FreeVector):
	@overload
	def __init__(self, a: int, b: int):
		pass

	@overload
	def __init__(self, a: CardinalDirection):
		pass

	def __init__(self, a: int | CardinalDirection,
	             b: int | None = None):  # pyright: ignore [reportInconsistentOverload]
		if b is None:
			assert isinstance(a, CardinalDirection)
			RelativeFreeVector(a.dx, a.dy)
		else:
			assert isinstance(a, int)
			super().__init__(a, b)
			self.dx = a
			self.dy = b

	def mirrored(self):
		return FreeVector(-self.dx, -self.dy)

	def to_free_vector(self):
		return FreeVector(self.dx, self.dy)


class Move(FixedVector):
	@dataclass
	class Partial:
		kind: PieceKind | None = None
		initial_file: Letter | None = None
		initial_rank: int | None = None
		is_capture: bool | None = None
		final_file: Letter | None = None
		final_rank: int | None = None

		"""Returns true if there is any non-None value after the specified index"""

		def check_nones(self, from_name: str) -> bool:
			begin = False
			for name, value in asdict(self).items():
				if from_name == name:
					begin = True
				if begin and value is not None:
					return True

			return False

		def initial_might_eq(self, file: Letter, rank: int, kind: PieceKind):
			return might_eq(self.initial_file, file) and might_eq(self.initial_rank, rank) and might_eq(self.kind, kind)

		def final_might_eq(self, file: Letter, rank: int, capture: bool):
			return might_eq(self.final_file, file) and might_eq(self.final_rank, rank) and might_eq(self.is_capture,
			                                                                                        capture)

	class NotationBaseError(Exception):
		def __init__(self, message: str):
			self.message = message

	class MatchError(NotationBaseError):
		def __init__(self, sym: str):
			super().__init__(f"S'ha especificat '{sym}' però el moviment no ho compleix.")

	class AmbiguousMoveError(NotationBaseError):
		def __init__(self, moves: list[Move]):
			self.moves = moves

	def __init__(self, piece: Piece, origin: Board.Cell, dest: Board.Cell):
		self.piece = piece
		self.origin = origin
		self.dest = dest
		self.capture = dest.piece

		super().__init__(self.origin.obj.x, self.origin.obj.y, self.dest.obj.x, self.dest.obj.y, self.origin, self.dest)

	def __call__(self):
		self.piece.move(self)

	@staticmethod
	def query(s: str, team: Team) -> list[Move]:
		move: None | Move = None
		
		try:
			move = Move.from_notation(s, team)
		except Exception as e:
			if isinstance(e, Move.AmbiguousMoveError):
				return e.moves
		else:
			assert move
			return [move]
		return []
			
	@staticmethod
	def from_notation(s: str, team: Team) -> Move | None:
		"""
		Returns the Move object described by the provided string. The string must use algebraic notation and may use
		shortened versions. It is recommended to always provide the full form, since ambiguous moves will raise an error.

		If the piece kind is omitted, it is assumed that the move refers to the piece with the lowest score (in the case
		of traditional chess, the pawn).

		Capture symbol 'x' may always be omitted, but an error will be raised if it is included and the move does not
		actually capture a piece.

		Minimal algebraic notation, however, is not allowed; hence, the provided string must have a minimum length of 2.

		>>> Move.from_notation('a1', Team.WHITE), Move.from_notation('R1a3', Team.BLACK), Move.from_notation('Bxe5', Team.BLACK)

		@raise TypeError if the provided object is not a string or its length is not appropriate.
		@raise SyntaxError if the syntax is incorrect.
		@raise ArithmeticError if the move is illegal or would send the piece outside the board.
		@raise ValueError if the move does not capture a piece and the capture symbol was specified.
		@raise LookupError if the move is ambiguous, there is no piece that can be moved to the provided destination position
		or there is no piece in the provided origin position.
		@raise NameError if the provided piece kind does not exist.
		"""

		if not (isinstance(s, str) and 1 <= len(s) <= 6):
			raise TypeError

		partial = Move.Partial()

		for letter in s:
			if letter.isalpha():
				if letter == 'x':

					if partial.check_nones('is_capture'):
						raise SyntaxError

					partial.is_capture = True

					is_capture = True
				elif letter.isupper():
					if partial.check_nones('kind'):
						raise SyntaxError

					kind = PieceKind.from_letter(letter)

					if kind is None: raise NameError

					partial.kind = kind
				else:
					if partial.check_nones('initial_file'):
						if partial.check_nones('final_file'):
							raise SyntaxError
						
						try:
							partial.final_file = Letter[letter]
						except:
							raise SyntaxError
					else:
						try:
							partial.initial_file = Letter[letter]
						except:
							raise SyntaxError
			else:
				if partial.check_nones('initial_rank'):
					if partial.check_nones('final_rank'):
						raise SyntaxError
					try:
						partial.final_rank = int(letter) - 1
					except:
						raise SyntaxError
				else:
					try:
						partial.initial_rank = int(letter) - 1
					except:
						raise SyntaxError

		if partial.is_capture is None and partial.final_file is None and partial.final_rank is None:
			partial.final_rank = partial.initial_rank
			partial.initial_rank = None
			partial.final_file = partial.initial_file
			partial.initial_file = None

		moves: dict[Piece, list[Board.Cell]] = {}

		if (partial.initial_rank is None) != (partial.initial_file is None):
			q = partial.initial_file if partial.initial_rank is None else partial.initial_rank
			assert q is not None

			moves.update({c.piece: [m for m in c.piece.get_moves() if
			                        isinstance(m, Board.Cell) and partial.final_might_eq(m.obj.file, m.obj.rank,
			                                                                             bool(m.piece))] for c
			              in Board.query(q) if
			              c.piece and c.piece.team == team and partial.initial_might_eq(c.obj.file, c.obj.rank,
			                                                                            c.piece.kind)})

		elif partial.initial_rank is None and partial.initial_file is None:
			moves.update({p: [m for m in p.get_moves() if
			                  isinstance(m, Board.Cell) and partial.final_might_eq(m.obj.file, m.obj.rank,
			                                                                       bool(m.piece))] for p in
			              Board.pieces if p.team == team and p.cell and might_eq(partial.kind, p.kind)})
		else:
			assert partial.initial_rank is not None and partial.initial_file is not None

			origin = Coords(partial.initial_file, partial.initial_rank)
			try:
				cell = Board.get_cell(origin)
			except Exception:
				raise Move.NotationBaseError("Coordenades errònees")

			if cell.piece is None:
				raise Move.NotationBaseError("No hi ha cap peça a l'origen especificat")

			if cell.piece.team != team:
				raise Move.NotationBaseError("No pots moure una peça de l'altre jugador")

			if not might_eq(partial.kind, cell.piece.kind):
				raise Move.NotationBaseError("El tipus de peça indicat no es correspon amb la cel·la d'origen")

			for c in cell.piece.get_moves():
				if isinstance(c, Board.Cell) and partial.final_might_eq(c.obj.file, c.obj.rank, bool(c.piece)):
					if cell.piece not in moves:
						moves[cell.piece] = [c]
					else:
						moves[cell.piece].append(c)

		if len(moves) == 0:
			raise Move.NotationBaseError("Cap moviment possible")

		possible: list[Move] = []
		for p in list(moves.keys()):
			if len(moves[p]) > 0:
				for c in moves[p]:
					assert p.cell
					possible.append(Move(p, p.cell, c))

		if len(possible) > 1:
			raise Move.AmbiguousMoveError(possible)

		if len(possible) == 0:
			raise Move.NotationBaseError("Cap moviment possible")

		return possible[0]

	@staticmethod
	def from_vector(piece: Piece, v: RelativeFreeVector):
		assert piece.cell is not None

		return Move(piece, piece.cell, Board.get_cell(piece.cell.get(v)))

	@staticmethod
	def from_coords(piece: Piece, coords: Coords):
		assert piece.cell is not None

		return Move(piece, piece.cell, Board.get_cell(coords))

	@staticmethod
	def get_moves(p: Piece):
		assert p.cell
		return [Move(p, p.cell, c) for c in p.get_moves() if not isinstance(c, str)]

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
		if move.dest.piece is not None:
			move.dest.piece.cell = None
			self.team.score += move.dest.piece.kind.score

		self.place(move.dest)
		self.history.append(move)

	def is_move_possible(self, a: FreeVector | RelativeFreeVector | Board.Cell | Coords,
	                     captures: bool | None = None) -> Board.Cell | None:
		assert self.cell is not None

		coord = self.cell.get(a) if isinstance(a, RelativeFreeVector) else (
			self.cell.obj + a if isinstance(a, FreeVector) else (
				(a if isinstance(a, Coords) else a.obj)))
		is_within = Board.bounds.is_within(coord)
		if not is_within: return None

		cell = Board.get_cell(coord) if isinstance(a, (RelativeFreeVector, FreeVector)) else (
			Board.get_cell(a) if isinstance(a, Coords) else a)

		if captures:  # must capture
			return cell if cell.piece and cell.piece.team != self.team else None
		elif captures is None:  # may capture
			return None if cell.piece and cell.piece.team == self.team else cell
		else:  # must not capture
			return None if cell.piece else cell

	def get(self, v: RelativeFreeVector):
		pass

	def get_moves(self) -> list[Board.Cell | str]:
		assert self.cell

		destinations: list[Board.Cell | str] = []

		for m in self.kind.get_moves(self.team):
			if isinstance(m, CardinalDirection):
				destinations.extend(Board.get_points(self.cell.obj, m, self.team))

			else:
				if c := self.is_move_possible(m, captures=(False if self.kind.options.no_auto_capture else None)):
					destinations.append(c)

		if self.kind.special:
			special = list(self.kind.special(self).keys())
			for a in special:
				if isinstance(a, RelativeFreeVector):
					if c := self.is_move_possible(a, captures=None):
						destinations.append(c)
				else:
					destinations.append(a if isinstance(a, Board.Cell) else a)

		return destinations


class Team(Enum):
	WHITE = ('Y', "BLANC")
	BLACK = ('Z', "NEGRE", True)

	def __init__(self, id: str, locale: str, mirrored=False) -> None:
		self.id = id
		self.mirrored = mirrored
		self.locale = locale
		self.score = 0
		self.in_check = False
		super().__init__()

	@property
	def opponent(self) -> Team:
		if self is Team.WHITE:
			return Team.BLACK
		else:
			return Team.WHITE
		
	def get(self, k: PieceKind) -> list[Piece]:
		return [p for p in Board.pieces if p.kind == k and p.team == self]

	def __invert__(self) -> Team:
		return self.opponent


class Coords(Point):
	@overload
	def __init__(self, a: str):
		pass

	@overload
	def __init__(self, a: Letter, b: int):
		pass

	@overload
	def __init__(self, a: Point):
		pass

	@overload
	def __init__(self, a: int, b: int):
		pass

	def __init__(self, a: Point | Letter | int | str,
	             b: int | None = None):  # pyright: ignore [reportInconsistentOverload]
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
		return self.y

	def invert(self) -> Coords:
		return Board.get_cell(Board.bounds.get_mirrored_point(self, Direction.VERTICAL)).obj

	def __str__(self):
		return str(self.file.name) + str(self.rank + 1)

	def __add__(self, other: tuple[int, int] | Vector) -> Coords:
		return Coords(super().__add__(other))


class PieceKindOptions:
	def __init__(self, no_auto_capture: bool = False) -> None:
		self.no_auto_capture = no_auto_capture


# class SpecialMovesList:
# 	def __init__(self, dests: list[Board.Cell | tuple[str, Callable[..., Board.Cell]]], override: bool = False):
# 		self.dests = dests
# 		self.override = override


def special_pawn(piece: Piece) -> Mapping[Board.Cell | RelativeFreeVector, None]:
	assert piece.cell is not None

	moves: list[Board.Cell | RelativeFreeVector] = []

	if len(piece.history) == 0:
		if c := piece.is_move_possible(RelativeFreeVector(0, 2), captures=False):
			moves.append(c)

	for v in [RelativeFreeVector(1, 1), RelativeFreeVector(-1, 1)]:
		if c := piece.is_move_possible(v, captures=True):
			moves.append(c)

	return {m: None for m in moves}


# TODO: Metaclasses?
class PieceKind(Enum):
	PAWN = (
		"peó", 'P', 1, ('♟', '♙'), ["a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2"], [FreeVector(0, 1)], special_pawn)
	KNIGHT = ("cavall", 'C', 3, ('♞', '♘'), ["b1", "g1"], CardinalDirection.get_rotations(1, 2), None)
	BISHOP = ("alfil", 'A', 5, ('♝', '♗'), ["c1", "f1"], CardinalDirection.D_CROSS())
	ROOK = ("torre", 'T', 5, ('♜', '♖'), ["a1", "h1"], CardinalDirection.CROSS())
	QUEEN = ("reina", 'D', 9, ('♛', '♕'), "d1", CardinalDirection.ALL())
	KING = (
		"rei", 'R', 10, ('♚', '♔'), "e1",
		[*CardinalDirection.get_rotations(1, 0), *CardinalDirection.get_rotations(1, 1)])

	def __init__(self, name: str, short: str, score: int, icon: tuple[str, str],
	             initial_pos: Coords | str | Sequence[Coords | str],
	             moves: Sequence[FreeVector | CardinalDirection],
	             special: Callable[[Piece], Mapping[Board.Cell | RelativeFreeVector, None]] | Callable[
		             [Piece], Mapping[str, Callable]] | None = None,
	             options: PieceKindOptions = PieceKindOptions()
	             ) -> None:
		self._name = name
		self.short = short
		self.score = score
		self.icon = {Team.WHITE: icon[0], Team.BLACK: icon[1]}
		self.initial_pos = [(p if isinstance(p, Coords) else Coords(p))
		                    for p in ([initial_pos] if isinstance(initial_pos, str) or isinstance(initial_pos,
		                                                                                          Coords) else initial_pos)]
		self.moves = [m if isinstance(m, CardinalDirection) else RelativeFreeVector(m.dx, m.dy) for m in moves]
		self.special = special
		self.options = options

	def __call__(self) -> list[Piece]:
		return [Piece(Team.WHITE, self, Board.get_cell(p)) for p in self.initial_pos] + [
			Piece(Team.BLACK, self, Board.get_cell(Board.bounds.get_mirrored_point(p, Direction.VERTICAL))) for p in
			self.initial_pos]

	def get_moves(self, team: Team) -> Sequence[FreeVector | CardinalDirection]:
		return [m if isinstance(m, CardinalDirection) else (m.mirrored() if team.mirrored else m.to_free_vector()) for m
		        in self.moves]

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

		def __repr__(self):
			return self.__str__()

	matrix: list[list[Cell]]
	bounds: Bounds = Bounds(0, 0, 8, 8)
	pieces: list[Piece]

	@classmethod
	def get_points(cls, origin: Coords, v: CardinalDirection, team: Team) -> list[Cell]:
		l = []
		i = 1
		if team.mirrored:
			v = v.mirrored()
		while True:
			try:
				d = (origin + v.vector * i)
				if not cls.bounds.is_within(d):
					break

				c = cls.get_cell(d)

				if c.piece is not None and c.piece.team == team:
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
	def init(cls) -> list[Piece]:
		cls.matrix: list[list[Board.Cell]] = [[Board.Cell(Point(j, i)) for j in range(cls.bounds.width)] for i in
		                                      range(cls.bounds.height)]
		cls.pieces: list[Piece] = []
		for kind in PieceKind:
			cls.pieces.extend(kind())
			
		for t in Team:
			t.score = 0
			t.in_check = False

		return cls.pieces

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
	def get_cell(cls, a: Cell | Point | str | int,  # pyright: ignore [reportInconsistentOverload]
	             b: RelativeFreeVector | int | None = None) -> Board.Cell:  # pyright: ignore [reportInconsistentOverload]
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

		return cls.get_cell(a.x, a.y)

	@classmethod
	def is_move_possible(cls, origin: Cell, d: RelativeFreeVector):
		assert origin.piece
		c = cls.get_cell(origin, d)
		return c is not None and cls.bounds.is_within(c.obj) and (not c.piece or c.piece.team != origin.piece.team)

	@classmethod
	def query(cls, a: Letter | int, team: Team | bool | None = None, inv=False) -> list[Board.Cell]:
		"""

		@param team: if it's a boolean, returns empty cells. If it's None, returns all cells.
		@param inv: inverts the condition
		"""
		l: list[Board.Cell] = []

		return [c for c in ([c[a.value] for c in cls.matrix] if isinstance(a, Letter) else cls.matrix[a]) if
		        (team is None or (
			        (not c.piece) if isinstance(team, bool) else c.piece and c.piece.team == team)) != inv]

	def __class_getitem__(cls, c: str) -> Board.Cell | None:
		return cls.get_cell(c)

	@classmethod
	def render(cls, highlight: list[Cell] | None = None):
		if highlight is None:
			highlight = []
		s = "  "

		for i in range(cls.bounds.width):
			s += Colors.gris(Letter(i).name) + " "

		s += '\n'
		i = cls.bounds.height

		for row in cls.matrix[::-1]:
			s += Estils.negreta(Colors.gris(str(i))) + " "

			for p in row:
				s += ((lambda ic: Estils.invers(ic) if p in highlight else ic)(
					p.piece.kind.icon[p.piece.team]) + ' ' if p.piece else (
					Estils.invers(' ') + ' ' if p in highlight else "  "))

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


thisBoard = BoardAlias()
