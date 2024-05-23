# class Classe:
# 	b = 2
# 	def __init__(self) -> None:
# 		self.c = 3
# 
# instància = Classe()
# 
# def mostrar():
# 	print("inst.b =", instància.b)
# 	print("A.b =", Classe.b)
# 	print()
# 
# print("b = 2")
# print()
# 
# print("Modificar atribut de classe")
# Classe.b = 4
# mostrar()
# 
# print("Modificar atribut de classe")
# Classe.b = 5
# mostrar()
# 
# print("Modificar atribut d'instància (inexistent)")
# instància.b = 6
# mostrar()
# 
# print("Modificar atribut de classe")
# Classe.b = 7
# mostrar()
from enum import Enum

from board import Board
from plane import Bounds, Direction

bounds = Bounds(0, 0, 8, 8)
print(bounds.height)
board = Board(bounds)

cell = board["a1"]

print(cell)

print(cell.obj.invert(board))

print(board)
