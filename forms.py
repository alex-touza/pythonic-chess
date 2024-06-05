from collections.abc import Callable
from typing import Any, TypeVar
from os import system, name
from abc import ABCMeta, abstractmethod

from text import Colors, Estils

T = TypeVar('T')

def quant(n: int, singular: str, plural: str) -> str:
	return f"Cap {singular}" if n == 0 else (f"1 {singular}" if n == 1 else f"{n} {plural}")

class Formulari(metaclass=ABCMeta):

	@abstractmethod
	def __call__(self) -> Any:
		pass


def clear():
	if name == 'nt':
		system('cls')
	else:
		system('clear')


def _input(missatge=""):
	a = input(missatge + Colors.groc_fosc)
	Colors.reset()
	return a


def error(missatge):
	print(Colors.vermell(missatge))


def pausar(nova_linia=False):
	if nova_linia:
		print()
	input("Prem enter per continuar..." + Colors.groc_fosc)
	Colors.reset()


def titol(text: str, _clear=False):
	if _clear:
		clear()
	print(Estils.negreta(text))
	print("----------------")

def title(text: str, _clear=False):
	titol(text, _clear)

class Opcio(Formulari):
	"""
	Crea un formulari amb opcions, reutilitzable simplement cridant una instància.

	"""

	def __init__(self,
							 missatge: str | None,
							 opcions,
							 args=None,
							 descr: str | None = None,
							 enrere: str | None = "Enrere",
							 refrescar=True,
							 mostrar=True,
							 sep: str | None = "----------------"):
		"""
		- opcions: Diccionari de les opcions, on les claus són els noms de les opcions i els valors són les funcions
		associades. Allò que retornin és ignorat. El tipus no està anotat per la seva complexitat.
		- args: L'argument amb el qual es cridaran les funcions.
		"""
		self.missatge = missatge
		self.descr = descr
		self.opcions = opcions
		self.args = args
		self.enrere = enrere
		self.refrescar = refrescar
		self.mostrar = mostrar
		self.sep = sep

	# Retorna l'índex de l'opció escollida.
	def __call__(self) -> int:
		if self.refrescar:
			clear()

		if self.missatge is not None:
			print(Estils.negreta(self.missatge))

		if self.sep is not None:
			print(self.sep)

		if self.descr is not None:
			print(self.descr)

		# Colors.blau()

		if self.mostrar:
			if self.enrere is not None:
				print(f"0. {self.enrere}")
			for i, opcio in enumerate(self.opcions.keys(), 1):
				print(f"{i}. {opcio}")

		# Colors.reset()

		op = _input()
		if self.enrere is not None and (op == "" or op == "0"):
			return 0
		elif op.isdigit() and int(op) in range(1, len(self.opcions) + 1):
			c = int(op)
			# Executar funció associada a l'opció amb els arguments
			v = list(self.opcions.values())[c - 1]

			if v is not None:
				if self.args is None:
					v()
				else:
					v(self.args)

			return c
		else:
			print(Colors.vermell("Opció invàlida.\n"))
			# Tornar a escollir. Recursivitat, yay.
			return self()


class Text(Formulari):

	def __init__(self,
							 missatge: str,
							 comprovar: Callable[[str, int], bool] = (lambda t, le: True),
							 sufix=": ",
							 buit=False, default: str | None=""):
		"""
		- missatge: Títol del formulari.
		- comprovar: Funció que ha de retornar un booleà indicant si el text introduït
			és vàlid. El primer argument és el text i el segon la llargada.
		- buit: Permet un valor buit com a resposta.
		- default: Valor per defecte si el valor sense espais és buit. Requereix buit=True
		"""
		self.missatge = missatge
		self.sufix = sufix
		self.comprovar = comprovar
		self.buit = buit
		self.default = default

	def __call__(self) -> str | None:
		text = _input(("" if self.missatge is None else
									 (self.missatge + self.sufix))).strip()


		valid = (text != ""
						 and self.comprovar(text, len(text))) or (self.buit and text == "")
		# Taula de veritat
		# self.buit    text == ""   self.comprovar     *valid*
		#     0           0              0                0
		#     0           0              1                1
		#     0           1              0                0
		#     0           1              1                0
		#     1           0              0                0
		#     1           0              1                1
		#     1           1              0                1
		#     1           1              1                1
		#

		if not valid:
			error("Text invàlid.")
			return self()
		return self.default if text == "" else text


class Nombre(Formulari):

	def __init__(self,
							 missatge: str | None = "",
							 comprovar1: Callable[[int], bool] = lambda n: True,
							 comprovar2: Callable[[int], bool] | None = None,
							 error_compr1: str = "Valor invàlid.",
							 error_compr2: str | None = "Valor invàlid.",
							 error_valor: str = "Valor invàlid.",
							 sufix=": ",
							 buit=False):
		self.buit = buit
		self.sufix = sufix
		self.comprovar1 = comprovar1
		self.comprovar2 = comprovar2
		self.missatge = missatge
		self.error_compr1 = error_compr1
		self.error_compr2 = error_compr2
		self.error_valor = error_valor

	def __call__(self) -> int | None:
		n = _input(("" if self.missatge is None else (self.missatge + self.sufix)))
		nint: None | int = None

		if n == "" and self.buit:
			return None

		try:
			nint = int(n)
		except Exception:
			error(self.error_compr1)
			return self()

		if self.comprovar1(nint):
			if self.comprovar2 is None or self.comprovar2(nint):
				return nint
			else:
				error(self.error_compr2)
		else:
			error(self.error_compr1)

		return self()


class Decisio(Opcio):

	def __init__(self,
							 missatge: str | None = "",
							 refrescar=True,
							 si="Sí",
							 no="No",
							 sep: str | None = "----------------",
							 descr: str | None = None):
		super().__init__(missatge, {si: None}, None, descr, no, refrescar, sep=sep)

	def __call__(self) -> bool:
		return super().__call__() == 1


class GrupFormularis:
	# Cal que tots els formularis tinguin la propietat "buit" com a True
	# perquè funcioni el paràmetre "opcional"
	def __init__(self, forms: dict[str, Formulari], opcional=False, permet_buits: list[int] = []) -> None:
		self.forms = forms
		self.opcional = opcional
		self.permet_buits = permet_buits
		pass

	def __call__(self) -> None | dict[str, Any]:
		resultats = {k: None for k in self.forms}

		for i, (k, f) in enumerate(self.forms.items()):
			r = None
			r = f()

			while r is None and not self.opcional:
				r = f()

			if r is None or (r == "" and not self.permet_buits.count(i)):
				return None
			else:
				resultats[k] = r

		return resultats

A = TypeVar('A')

# Totes les lambdes reben la llista de valors i l'últim valor com a arguments
def mentre(form: Formulari, callback: Callable[[A, list[A]], Any] | None = None, stop_valors: tuple = (), stop_cond: Callable[[A, list[A]], bool] = lambda v, lv: False) -> list[A]:

	lv = []
	valor = form()

	while valor not in stop_valors and valor not in ("", None):
		lv.append(valor)
		if callback is not None: callback(valor, lv)

		if stop_cond(valor, lv):
			break

		valor = form()

	return lv