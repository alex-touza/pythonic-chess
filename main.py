from enum import Enum
from typing import Sequence

from board import *
from plane import Bounds, Direction

def f(l: Sequence[int | str]):
	print(isinstance(l, Sequence))


f(["a", 1])

bounds = Bounds(0, 0, 8, 8)

Board.init(bounds)

print(bounds.height)

print(board)

m = Move.from_notation("a1a3")

c = board["b7"]
assert c is not None

print([str(m) for m in c.piece.get_moves()])

c.piece.place(board["b6"])

board["b6"]




print(board)
