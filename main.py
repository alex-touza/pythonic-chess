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
from board import Board
from plane import Bounds

board = Board(Bounds(0, 0, 8, 8))

print('a'+1)