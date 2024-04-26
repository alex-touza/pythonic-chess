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

from plane import Directions, FixedVector, Point, Ref, Vector

O = Ref("O", Point(0, 0))
P = Ref("P", Point(2, 1))
Q = Ref("Q", Point(3, 4))

PQ = FixedVector.from_ref_points(P, Q)
V = Ref("V", FixedVector(0, 0, 1, 1))

print(O)
print(PQ)
print(V.obj.to_fixed(P))

print()
print(Directions.get_rotations(1, 1))

