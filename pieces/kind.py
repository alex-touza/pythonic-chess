from abc import ABC, abstractmethod

class FigureKind(ABC):
	
	@property
	@abstractmethod
	def movements(self) -> int:
		pass