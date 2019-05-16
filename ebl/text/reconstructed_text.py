from abc import ABC, abstractmethod
from enum import unique, Enum
from typing import Tuple, Optional

import attr


@unique
class Modifier(Enum):
    BROKEN = '#'
    UNCERTAIN = '?'


class BrokenOff(Enum):
    pass


@unique
class BrokenOffOpen(BrokenOff):
    BOTH = '[('
    BROKEN = '['
    MAYBE = '('


@unique
class BrokenOffClose(BrokenOff):
    BOTH = ')]'
    BROKEN = ']'
    MAYBE = ')'


@attr.s(frozen=True)
class Part(ABC):

    @property
    @abstractmethod
    def is_text(self) -> bool:
        ...


@attr.s(auto_attribs=True, frozen=True)
class StringPart(Part):
    _value: str

    @property
    def is_text(self) -> bool:
        return True

    def __str__(self) -> str:
        return self._value


@attr.s(auto_attribs=True, frozen=True)
class BrokenOffPart(Part):
    _value: BrokenOff

    @property
    def is_text(self) -> bool:
        return False

    def __str__(self) -> str:
        return self._value.value


@attr.s(auto_attribs=True, frozen=True)
class AkkadianWord:

    parts: Tuple[Part, ...]
    modifiers: Tuple[Modifier, ...] = tuple()

    def __str__(self) -> str:
        modifier_string = ''.join([modifier.value
                                   for modifier in self.modifiers])

        def create_string_without_final_broken_off() -> str:
            return ''.join([str(part) for part in self.parts]) +\
                   modifier_string

        def create_string_with_final_broken_off() -> str:
            return ''.join([str(part) for part in self.parts[:-1]]) +\
                   modifier_string + str(self.parts[-1])

        last_part = self.parts[-1]
        return (create_string_without_final_broken_off()
                if last_part.is_text
                else create_string_with_final_broken_off())


@attr.s(auto_attribs=True, frozen=True)
class Lacuna:
    _broken_off: Tuple[Optional[BrokenOffOpen], Optional[BrokenOffClose]]

    def __str__(self):
        return ''.join(self._generate_parts())

    def _generate_parts(self):
        if self._broken_off[0]:
            yield self._broken_off[0].value
        yield '...'
        if self._broken_off[1]:
            yield self._broken_off[1].value


@attr.s(auto_attribs=True, frozen=True)
class Break(ABC):
    uncertain: bool

    @property
    @abstractmethod
    def _value(self):
        ...

    def __str__(self) -> str:
        return f'({self._value})' if self.uncertain else self._value


@attr.s(frozen=True)
class Caesura(Break):

    @property
    def _value(self):
        return '||'


@attr.s(frozen=True)
class MetricalFootSeparator(Break):

    @property
    def _value(self):
        return '|'
