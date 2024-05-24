from typing import Any, Generic, Optional, Type, TypeVar, get_args, get_origin


# The `GenericBase` must be parameterized with exactly one type variable.
T = TypeVar("T")
Q = TypeVar('A', bound='BaseClass')

class BaseClass:
	def hi_base(self):
		pass

class DerivedClass(BaseClass):
	def hi_derived(self):
		pass


class GenericBase(Generic[T]):
		_type_arg: Optional[Type[T]] = None  # set in specified subclasses

		@classmethod
		def __init_subclass__(cls, **kwargs: Any) -> None:
				"""
				Initializes a subclass of `GenericBase`.

				Identifies the specified `GenericBase` among all base classes and
				saves the provided type argument in the `_type_arg` class attribute
				"""
				super().__init_subclass__(**kwargs)
				for base in cls.__orig_bases__:  # type: ignore[attr-defined]
						origin = get_origin(base)
						if origin is None or not issubclass(origin, GenericBase):
								continue
						type_arg = get_args(base)[0]
						# Do not set the attribute for GENERIC subclasses!
						if not isinstance(type_arg, TypeVar):
								cls._type_arg = type_arg
								return

		@classmethod
		def get_type_arg(cls) -> Type[T]:
				if cls._type_arg is None:
						raise AttributeError(
								f"{cls.__name__} is generic; type argument unspecified"
						)
				return cls._type_arg


def demo_a() -> None:
		class SpecificA(Generic[T]):
				def __init__(self, s: T):
					self.s = s

		a = SpecificA(DerivedClass())

		print(SpecificA.get_type_arg())


def demo_b() -> None:
		class Foo:
				pass

		class Bar:
				pass

		class GenericSubclass(GenericBase[T]):
				pass

		class SpecificB(Foo, GenericSubclass[str], Bar):
				pass

		type_b = SpecificB.get_type_arg()
		print(type_b)
		e = type_b.lower("E")  # static type checkers correctly infer `str` type
		assert e == "e"


if __name__ == '__main__':
		demo_a()
		demo_b()