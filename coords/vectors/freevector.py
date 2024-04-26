
class FreeVector:
	def __init__(self, dx: int, dy: int):
		self.dx = dx
		self.dy = dy

	@classmethod
	def from_point(cls, p: Point):
		return cls(p.x, p.y)

	@classmethod
	def from_fixed(cls, v: FixedVector):
		return cls(v.x2 - v.x1, v.y2 - v.y1)

	@classmethod
	def from_delta(cls, dx: int, dy: int):
		return cls(dx, dy)

	def to_fixed(self, o: Point = Point(0, 0)):
		return FixedVector.from_point_vector(o, self)

	def __str__(self):
		return f"({self.dx}, {self.dy})"