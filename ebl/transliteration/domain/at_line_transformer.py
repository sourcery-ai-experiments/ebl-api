from dataclasses import dataclass
from typing import List

from lark import Token
from lark.visitors import Transformer, v_args

from ebl.transliteration.domain import atf
from ebl.transliteration.domain.at_line import (
    ColumnAtLine,
    CompositeAtLine,
    DiscourseAtLine,
    DivisionAtLine,
    HeadingAtLine,
    ObjectAtLine,
    SealAtLine,
    SurfaceAtLine,
)
from ebl.transliteration.domain.labels import ColumnLabel, SurfaceLabel


@dataclass
class ObjectData:
    object: atf.Object
    text: str = ""


class AtLineTransformer(Transformer):
    def ebl_atf_at_line__free_text(self, content: List[Token]):
        return "".join(content)

    @v_args(inline=True)
    def ebl_atf_at_line__INT(self, number):
        return int(number)

    @v_args(inline=True)
    def ebl_atf_at_line__LCASE_LETTER(self, letter):
        return str(letter)

    @v_args(inline=True)
    def ebl_atf_at_line__STATUS(self, status):
        return atf.Status(status)

    @v_args(inline=True)
    def ebl_atf_at_line__seal(self, number):
        return SealAtLine(number)

    @v_args(inline=True)
    def ebl_atf_at_line__column(self, number, statuses):
        return ColumnAtLine(ColumnLabel.from_int(number, statuses.children))

    @v_args(inline=True)
    def ebl_atf_at_line__discourse(self, discourse):
        return DiscourseAtLine(atf.Discourse(discourse))

    @v_args(inline=True)
    def ebl_atf_at_line__heading(self, number):
        return HeadingAtLine(number)

    @v_args(inline=True)
    def ebl_atf_at_line__OBJECT(self, object_: Token):
        return ObjectData(atf.Object(object_))

    @v_args(inline=True)
    def ebl_atf_at_line__generic_object(self, text: str):
        return ObjectData(atf.Object.OBJECT, text,)

    @v_args(inline=True)
    def ebl_atf_at_line__fragment(self, text: str):
        return ObjectData(atf.Object.FRAGMENT, text)

    @v_args(inline=True)
    def ebl_atf_at_line__SURFACE(self, surface: Token):
        return SurfaceLabel.from_label(atf.Surface.from_atf(surface))

    @v_args(inline=True)
    def ebl_atf_at_line__generic_surface(self, text: str):
        return SurfaceLabel.from_label(atf.Surface.SURFACE, text=text)

    @v_args(inline=True)
    def ebl_atf_at_line__face(self, text: Token):
        return SurfaceLabel.from_label(atf.Surface.FACE, text=str(text))

    @v_args(inline=True)
    def ebl_atf_at_line__edge(self, text: str = ""):
        return SurfaceLabel.from_label(atf.Surface.EDGE, text=text)

    @v_args(inline=True)
    def ebl_atf_at_line__surface_with_status(self, surface: SurfaceLabel, statuses):
        return SurfaceAtLine(
            SurfaceLabel(statuses.children, surface.surface, surface.text)
        )

    @v_args(inline=True)
    def ebl_atf_at_line__object_with_status(self, object_: ObjectData, statuses):
        return ObjectAtLine(statuses.children, object_.object, object_.text)

    @v_args(inline=True)
    def ebl_atf_at_line__divisions(self, text, digit):
        return DivisionAtLine(text, digit)

    @v_args(inline=True)
    def ebl_atf_at_line__composite_start(self, text, number):
        return CompositeAtLine(atf.Composite.DIV, text, number)

    @v_args(inline=True)
    def ebl_atf_at_line__composite_end(self, text):
        return CompositeAtLine(atf.Composite.END, text)
