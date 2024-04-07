from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Punt:
	x: int
	y: int

	def __add__(self, other: tuple[int, int] | Punt):
		isobj = isinstance(other, Punt)

		_x = other.x if isobj else other[0]
		_y = other.y if isobj else other[1]

		nextX = self.x + _x
		nextY = self.y + _y

		if not (0 < nextX < 7 and 0 < nextY < 7):
			raise Exception
		else:
			self.x = nextX
			self.y = nextY