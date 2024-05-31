from enum import Enum

from board import *
from plane import Bounds, Direction

bounds = Bounds(0, 0, 8, 8)
print(bounds.height)
board = Board(bounds)

print(board)

m = Move.from_notation("a1a3", board)

c = board["b7"]
assert c is not None

print([str(m) for m in c.piece.get_moves()])

c.piece.place(board["b6"])

print(board)