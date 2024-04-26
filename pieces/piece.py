from enum import Enum
from typing import Sequence
from ..plane import DirectionVector, Directions, FreeVector, Point, Ref
from abc import ABC, abstractmethod

class Team(Enum):
	WHITE = 'Y'
	BLACK = 'Z'

class PieceKind(Enum):
	PAWN = ("peó", 'P', 1, ('♟', '♙'), [FreeVector(0, 1)], [FreeVector(1,1), FreeVector(-1, 1)])
	KNIGHT = ("cavall", 'C', 3, ('♞', '♘'),  Directions.get_rotations(1, 2))
	BISHOP = ("alfil", 'A', 5, ('♝', '♗'), [d.rotate_left(1) for d in Directions.CROSS()])
	ROOK = ("torre", 'T', 5, ('♜', '♖'),  Directions.CROSS())
	QUEEN = ("reina", 'D', 9, ('♛', '♕'), Directions.ALL())
	KING = ("rei", 'R', 10, ('♚', '♔'), [*Directions.get_rotations(1, 0), *Directions.get_rotations(1,1)])
	
	def __init__(self, name: str, short: str, values: int, icon: tuple[str, str], moves: Sequence[FreeVector | Directions], attack: Sequence[FreeVector | Directions] | None = None) -> None:
		self._name = name
		self.short = short
		self.values = values
		self.moves = moves
		self.attack = attack
		self.icon = icon
		super().__init__()


class Piece(Ref[Point]):
	def __init__(self, team: Team, kind: PieceKind, pos: Point):
		self.team = team
		self.kind = kind
		self.pos = pos
		
		super().__init__(self.team.value + self.kind.short, self.pos)