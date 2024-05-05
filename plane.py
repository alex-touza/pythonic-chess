from __future__ import annotations
from enum import Enum
from typing import Generic, TypeVar, Callable, MutableSequence, Type, overload, Literal
from dataclasses import dataclass, fields
from abc import ABC, abstractmethod
from math import sqrt

Obj = TypeVar("Obj", "FreeVector", "FixedVector", "DirectionVector", "Point")
T = TypeVar('T')


class Unit(int):
	def __new__(cls, value: Literal[0, 1, -1] | int):
		if isinstance(value, cls):
			return value

		if value < -1:
			value = -1

		if value > 1:
			value = 1

		return super().__new__(cls, value)

	def __neg__(self) -> Unit:
		return Unit(super().__neg__())


@dataclass
class Point:
	x: int
	y: int

	def __add__(self, other: tuple[int, int] | Vector) -> Point:
		isvector = isinstance(other, Vector)
		return Point(self.x + (other._x if isvector else other[0]), self.y + (other._y if isvector else other[1]))

	def __str__(self):
		return f"({self.x}, {self.y})"


class Bounds:
	def __init__(self, x1: int, y1: int, x2: int, y2: int):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

	def __call__(self, obj: Point) -> bool:
		return self.is_within(obj)

	def is_within(self, obj: Point) -> bool:
		return self.x1 <= obj.x <= self.x2 and self.y1 <= obj.y <= self.y2

	def get_points(self, all=True) -> list[Point]:
		return [Point(self.x1, self.y1), Point(self.x2, self.y2)] + (
			[Point(self.x1, self.y2), Point(self.x2, self.y1)] if all else [])

	@property
	def width(self):
		return self.x2 - self.x1 + 1

	@property
	def height(self):
		return self.y2 - self.y1 + 1


class Vector(ABC):

	@abstractmethod
	def __init__(self) -> None:
		pass

	@abstractmethod
	def __add__(self, b: Vector) -> Vector:
		pass

	@abstractmethod
	def __mul__(self, c: int) -> Vector:
		pass

	def __eq__(self, other: Vector) -> bool:
		return self._x == other._x and self._y == other._y

	@abstractmethod
	def __str__(self) -> str:
		pass

	@property
	@abstractmethod
	def _x(self) -> int:
		pass

	@property
	@abstractmethod
	def _y(self) -> int:
		pass

	@abstractmethod
	def squared_magnitude(self) -> int:
		pass

	@abstractmethod
	def magnitude(self) -> float:
		pass

	def slope(self) -> float:
		return self._y / self._x


class FreeVector(Vector):
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

	def to_fixed(self, o: Point | tuple[int, int] = Point(0, 0)):
		return FixedVector.from_point_vector(o if isinstance(o, Point) else Point(*o), self)

	def to_tuple(self):
		return (self.dx, self.dy)

	def squared_magnitude(self) -> int:
		return self.dx ** 2 + self.dy ** 2

	def magnitude(self) -> float:
		return sqrt(self.squared_magnitude())

	def __add__(self, other: Vector):
		return FreeVector(self.dx + other._x, self.dy + other._y)

	def __mul__(self, c: int):
		return FreeVector(self.dx * c, self.dy * c)

	def __str__(self):
		return f"({self.dx}, {self.dy})"

	def __repr__(self) -> str:
		return self.__str__()

	@property
	def _x(self) -> int:
		return self.dx

	@property
	def _y(self) -> int:
		return self.dy


class FixedVector(Vector):
	def __init__(self, x1: int, y1: int, x2: int, y2: int, start_ref: Ref[Point] | None = None,
	             end_ref: Ref[Point] | None = None) -> None:
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2

		self.start_ref = start_ref
		self.end_ref = end_ref

	@classmethod
	def from_points(cls, a: Point, b: Point) -> FixedVector:
		return cls(a.x, a.y, b.x, b.y)

	@classmethod
	def from_ref_points(cls, a: Ref[Point], b: Ref[Point]) -> Ref[FixedVector]:
		return Ref(a.name + b.name, cls(a.obj.x, a.obj.y, b.obj.x, b.obj.y, a, b))

	@classmethod
	def from_point_vector(cls, a: Point | Ref[Point], d: FreeVector) -> FixedVector:
		_a = Ref.unref(a)
		return cls(_a.x, _a.y, _a.x + d.dx, _a.y + d.dy, a)

	def to_free(self):
		return FreeVector.from_fixed(self)

	def to_tuple(self):
		return self.dx, self.dy

	def to_fixed(self, p: Point | Ref[Point]):
		_p = Ref.unref(p)
		return FixedVector(_p.x, _p.y, _p.x + self.dx, _p.y + self.dy)

	def squared_magnitude(self) -> int:
		return self.dx ** 2 + self.dy ** 2

	def magnitude(self) -> float:
		return sqrt(self.squared_magnitude())

	def __add__(self, other: Vector):
		return FixedVector(self.x1, self.y1, self.x2 + other._x,
		                   self.y2 + other._y)

	def __mul__(self, c: int) -> Vector:
		return FixedVector(self.x1, self.y1, self.x1 + self.dx * c, self.y1 + self.dy * c, self.start_ref)

	def __str__(self):
		return f"({self.x1}, {self.y1}) -> ({self.x2}, {self.y2})"

	@property
	def dx(self) -> int:
		return self.x2 - self.x1

	@property
	def dy(self) -> int:
		return self.y2 - self.y1

	@property
	def _x(self) -> int:
		return self.dx

	@property
	def _y(self) -> int:
		return self.dy

	def start(self) -> Point:
		return Point(self.x1, self.y1)

	def end(self) -> Point:
		return Point(self.x2, self.y2)


class DirectionVector(Vector):
	def __init__(self, origin: Point | Ref[Point], dx: int, dy: int):
		self.origin = origin
		self.dx = dx
		self.dy = dy

	@classmethod
	def from_points(cls, a: Point, b: Point):
		return cls(a, b.x - a.x, b.y - a.y)

	@classmethod
	def from_fixed(cls, v: FixedVector):
		return cls(Point(v.x1, v.y1), v.x2 - v.x1, v.y2 - v.y1)

	@classmethod
	def from_point_vector(cls, a: Point | Ref[Point], d: FreeVector):
		_a = Ref.unref(a)
		return cls(_a, d.dx, d.dy)

	@classmethod
	def factory_from_point(cls, dx: int, dy: int) -> Callable[[Point | Ref[Point]], DirectionVector]:
		return lambda p: cls(p, dx, dy)

	def __call__(self, c: int) -> FixedVector:
		p = Ref.unref(self.origin)

		return FixedVector(p.x, p.y, p.x + self.dx * c, p.y + self.dy * c,
		                   self.origin if isinstance(self.origin, Ref) else None)

	def to_fixed(self, o: Point | None = None):
		return FixedVector.from_point_vector(self.origin if o is None else o, self.to_free())

	def to_free(self):
		return FreeVector(self.dx, self.dy)

	def to_callable(self) -> Callable[[Point], DirectionVector]:
		return lambda p: DirectionVector(p, self.dx, self.dy)

	def squared_magnitude(self) -> int:
		return self.dx ** 2 + self.dy ** 2

	def magnitude(self) -> float:
		return sqrt(self.squared_magnitude())

	def __str__(self) -> str:
		return f"origin({self.origin.x}, {self.origin.y}); delta({self.dx}, {self.dy})"

	def __mul__(self, c: int):
		return DirectionVector(self.origin, self.dx * c, self.dy * c)

	def __add__(self, b: Vector):
		return DirectionVector(self.origin, self.dx + b._x, self.dy + b._y)

	@property
	def _x(self) -> int:
		return self.dx

	@property
	def _y(self) -> int:
		return self.dy


class Direction(Enum):
	NORTH = 0, 1
	NORTH_EAST = 1, 1
	EAST = 1, 0
	SOUTH_EAST = 1, -1
	SOUTH = 0, -1
	SOUTH_WEST = -1, -1
	WEST = -1, 0
	NORTH_WEST = -1, 1

	def __init__(self, dx: Literal[-1, 0, 1], dy: Literal[-1, 0, 1]) -> None:
		self.dx = Unit(dx)
		self.dy = Unit(dy)
		self.vector = FreeVector(dx, dy)

	@staticmethod
	def ALL() -> MutableSequence[Direction]:
		return [Direction.NORTH, Direction.NORTH_EAST, Direction.EAST, Direction.SOUTH_EAST, Direction.SOUTH,
		        Direction.SOUTH_WEST, Direction.WEST, Direction.NORTH_WEST]

	@staticmethod
	def CROSS() -> MutableSequence[Direction]:
		return [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]

	@staticmethod
	def D_CROSS() -> MutableSequence[Direction]:
		return [Direction.NORTH_EAST, Direction.SOUTH_EAST, Direction.SOUTH_WEST, Direction.NORTH_WEST]

	@staticmethod
	def get_rotations(dx: int, dy: int) -> MutableSequence[FreeVector]:
		s: MutableSequence[FreeVector] = []

		for i in range(2):
			if i == 1 and dx == 0:
				break
			for j in range(2):
				if j == 1 and dy == 0:
					break
				x = dx * (1 - 2 * i)
				y = dy * (1 - 2 * j)

				s.append(FreeVector(x, y))

				if x != y:
					s.append(FreeVector(y, x))

		return s

	@staticmethod
	def from_index(ind: int):
		return Direction.ALL()[ind % 8]

	@staticmethod
	def from_coords(x: Unit, y: Unit):
		return [d for d in Direction.ALL() if d.dx == x and d.dy == y][0]

	@staticmethod
	def from_vector(v: Vector):
		return [d for d in Direction.ALL() if d.vector == v][0]

	@property
	def index(self):
		return Direction.ALL().index(self)

	def rotate_left(self, n=1):
		return self - n

	def rotate_right(self, n=1):
		return self + n

	def opposite(self):
		return self + 4

	def mirrored(self, east_west=False):
		return self.from_index(4 - self.index)

	def __add__(self, n: int):
		return self.from_index(self.index + n)

	def __sub__(self, n: int):
		return self + (-n)


class Ref(Generic[Obj]):

	# Functional references

	@staticmethod
	def set_name(obj: Obj, name: str):
		setattr(obj, "name", name)

	@staticmethod
	def set_ref(obj: Obj, ref: Ref):
		setattr(obj, "name", ref)

	@staticmethod
	def get_name(obj: Obj) -> str | None:
		return getattr(obj, "_name", None)

	@staticmethod
	def get_ref(obj: Obj) -> str | None:
		return getattr(obj, "_ref", None)

	@staticmethod
	def is_named(obj: Obj):
		return hasattr(obj, "_name")

	@staticmethod
	def is_refed(obj: Obj):
		return hasattr(obj, "_ref")

	# Object-oriented references

	@staticmethod
	def unref(obj: Obj | Ref[Obj]):
		return obj.obj if isinstance(obj, Ref) else obj

	def __init__(self, name: str, obj: Obj) -> None:
		Ref.set_name(obj, name)
		Ref.set_ref(obj, self)

		self.name = name
		self.obj = obj

	def __str__(self):
		return self.name + " " + str(self.obj)


class Plane:

	def __init__(self) -> None:
		self.points: list[Ref[Point]] = []
		self.vectors: list[Ref[FixedVector]] = []

	def push(self, ref: Ref[Point] | Ref[FixedVector]):
		if isinstance(ref.obj, Point):
			self.points.append(ref)
		elif isinstance(ref.obj, FixedVector):
			self.vectors.append(ref)

	def get(self, name: str, obj_type: Type[T]) -> T | None:
		arr = self.vectors if obj_type == Vector else self.points

		for ref in arr:
			if ref.name == name:
				return ref.obj

		return None

	def where(self, x: int, y: int) -> list[Ref[Point | FixedVector]]:
		return [ref for ref in self.points if ref.obj.x == x and ref.obj.y == y] + [ref for ref in self.vectors if
		                                                                            ref.obj.x1 == x and ref.obj.y1 == y]
