from typing import Optional, Sequence
import attr
from ebl.fragmentarium.domain.iso_date import DateWithNotes
from ebl.transliteration.domain.museum_number import MuseumNumber as ExcavationNumber
from ebl.corpus.domain.provenance import Provenance as ExcavationSite
from ebl.fragmentarium.domain.findspot import Findspot


@attr.s(auto_attribs=True, frozen=True)
class Archaeology:
    excavation_number: Optional[ExcavationNumber] = None
    site: Optional[ExcavationSite] = None
    regular_excavation: bool = True
    excavation_date: Sequence[DateWithNotes] = tuple()
    findspot_id: Optional[int] = None
    findspot: Optional[Findspot] = None
