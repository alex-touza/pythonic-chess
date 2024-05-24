from enum import Enum

from board import Board
from plane import Bounds, Direction

bounds = Bounds(0, 0, 8, 8)
print(bounds.height)
board = Board(bounds)

cell = board["a1"]

assert cell is not None

print(cell.obj.invert(board))

print(board)
