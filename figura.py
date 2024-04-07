from enum import Enum
from coordenades import Punt
from abc import ABC, abstractmethod, abstractproperty

class Figures(Enum):
	PEO = 0
	ALFIL = 1
	TORRE = 2
	CAVALL = 3
	REINA = 4
	REI = 5

class TipusFigura(ABC):
	@property
	@abstractmethod
	def moviments(self):
		pass

	
	

PUNTS = {
	Figures.PEO: 1,
	Figures.CAVALL: 3,
	Figures.ALFIL: 3,
	Figures.TORRE: 5,
	Figures.REINA: 9
}

class Figura(Punt):
	def __init__(self, tipus: Figures, coord: tuple[int, int]) -> None:
		self.tipus = tipus
		self.punts = PUNTS[self.tipus]
		
		super().__init__(*coord)