from collections.abc import Callable
from typing import Generic, TypeVar
from forms import Opcio, titol
from functools import wraps

T = TypeVar('T')  # Argument per cridar la funció per obtenir el titol
U = TypeVar('U')  # Tipus de la clau per mostrar les opcions. Pot ser un enum.


# Millores respecte a Biblioteca
# - Afegida funcionalitat d'eines dinàmiques
class Menu(Generic[T, U]):

	def __init__(self,
							 titol: str | Callable[[T], str],
							 arg: T | None = None,
							 enrere: str | None = "Enrere"):
		self._titol = titol
		self.titol_arg = arg
		self.enrere = enrere

		# Quan és True, l'administrador es tancarà encara que
		# no s'esculli "Enrere"
		self._sortir = False

	def sortir(self):
		self._sortir = True

	@property
	def titol(self) -> str:
		if callable(self._titol):
			assert self.titol_arg is not None
			return self._titol(self.titol_arg)
		else:
			return self._titol

	@staticmethod
	def menu(clau: Callable | None = None,
					 descr: str | Callable[..., str] | None = None):
		"""
		Mostra el menú amb les opcions que s'han configurat amb
		els decoradors. Totes les funcions paramètriques tenen com a
		argument la instància de la classe.
		El propi codi de la funció s'executa després de mostrar el
		títol i abans de mostrar les eines.
		L'existència del decorador permet escollir amb quin mètode
		el menú apareix.
		- clau: Funció  per determinar les eines que es mostren. Si és
		o retorna None, es mostren les eines amb la clau None.
		"""

		def dec(func):

			@wraps(func)
			def wrapper(self):  # self és la instància de la classe imperativa
				titol(self.titol, True)
				func(self)

				# https://stackoverflow.com/questions/34439/finding-what-methods-a-python-object-has

				_clau = clau(self) if callable(clau) else None

				# OBTENIR EINES ESTÀTIQUES

				# Filtrar els mètodes que tenen la clau corresponent i obtenir
				# l'ítem amb l'índex de l'ítem d'on s'ha obtingut si és una tupla
				def convertir(m) -> tuple[Callable | None, int]:
					c = getattr(m, 'clau', -1)
					if c == -1:
						return (None, -1)
					if type(c) == tuple:
						ind = None

						try:
							ind = c.index(_clau)
						except:  # La clau no és a la tupla. No es mostra.
							return (None, -1)

						# Trobar posició a la tupla en base a l'índex de la clau trobada
						return (m, m.pos[ind])
					elif c == _clau:

						# No és una tupla => m.pos és només un int
						return (m, m.pos)
					else:
						return (None, -1)

				# Obtenir tots els mètodes de la classe i les posicions.
				metodes = [
					convertir(m) for m in self.__class__.__dict__.values()
					if callable(m) and not getattr(m, 'amagada', False)
				]

				# Filtrar valors falsos
				metodes = list(filter(lambda x: x[0] is not None, metodes))

				# Ordenar els mètodes per la posició
				metodes.sort(key=lambda x: x[1])

				# Eliminar posició
				metodes = [m for m, i in metodes]

				assert all(callable(item) for item in metodes)

				# Obtenir el nom de l'opció i preparar la funció lambda que crida
				# la funció corresponent a opció amb els arguments corresponents,
				# sempre i quan la condició és nula o es compleix.
				op = {m.nom: m for m in metodes if m.cond is None or m.cond(self)}

				# OBTENIR EINES DINÀMIQUES

				# Obtenir mètodes marcats com a dinàmics
				metodes = [
					m for m in self.__class__.__dict__.values()
					if getattr(m, 'dinamic', False)
				]

				# Cridar les funcions per obtenir les eines dinàmiques
				for e in metodes:
					op.update(e(self))

				if Opcio(None,
								 op,
								 self, (descr(self) + '\n') if callable(descr) else
								 ((descr + '\n') if descr is not None else None),
								 refrescar=False,
								 enrere=self.enrere,
								 sep=None)() == 0:
					return 0
				else:
					_sortir = self._sortir
					self._sortir = False
					return not _sortir

			return wrapper

		return dec

	@staticmethod
	def tool(nom: str | None,
					 pos: int | tuple[int, ...],
					 clau: U | tuple[U] | None = None,
					 descr: str | None = None,
					 func_clau: str | None = None,
					 amagada: bool = False,
					 cond: Callable[..., bool] | None = None):
		"""
		Decorador que determina que una funció és una eina que forma
		part de l'administrador. Es mostrarà el títol amb el nom de
		l'eina i s'afegirà la funció a la llista d'eines amb la clau
		especificada.
		"""

		# La sintaxi dels decoradors amb arguments és innecessàriament i estúpidament
		#  complicada al python.
		# https://stackoverflow.com/questions/5929107/decorators-with-parameters

		# Generar decorador
		def dec(func):

			# Creador de la funció
			@wraps(func)
			def wrapper(self, *args, **kwargs):

				def amb_params(self, _nom, _descr, _func_clau, *args, **kwargs):
					if _func_clau is None:
						titol(self.titol + " - " + _nom, True)
						if _descr is not None:
							print(_descr)
						func(self, *args, **kwargs)
					else:
						getattr(self, _func_clau)()

				return amb_params(self, nom, descr, func_clau, *args, **kwargs)

			# self.eines[clau][nom] = lambda self: f(self, nom, descr, func)

			# Assegurar que clau i índex són els dos tuples o l'índex un nombre i la
			# clau no una tupla.
			assert type(clau) == type(pos) or (type(pos) == int
																				 and type(pos) != tuple)

			#  Afegir propietats a la pròpia funció per poder trobar-les
			#  més tard. Ignorar errors.
			wrapper.clau = clau
			wrapper.nom = nom
			wrapper.pos = pos
			wrapper.cond = cond
			wrapper.amagada = amagada

			return wrapper

		return dec

	@staticmethod
	def dynamic_tool(func: Callable[..., dict[str, Callable]]):
		func.dinamic = True
		return func