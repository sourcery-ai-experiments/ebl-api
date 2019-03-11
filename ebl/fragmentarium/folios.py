# pylint: disable=R0903
from typing import Tuple, Dict, List
import attr


@attr.s(auto_attribs=True, frozen=True)
class Folio:
    name: str
    number: str

    def to_dict(self) -> Dict[str, str]:
        return attr.asdict(self)


@attr.s(auto_attribs=True, frozen=True)
class Folios:
    entries: Tuple[Folio, ...] = tuple()

    def filter(self, user) -> 'Folios':
        folios = tuple(
            folio
            for folio in self.entries
            if user.can_read_folio(folio.name)
        )
        return Folios(folios)

    def to_list(self) -> List[Dict[str, str]]:
        return [folio.to_dict() for folio in self.entries]
