import attr
import pydash
import pytest

from ebl.auth0 import Guest
from ebl.corpus.alignment import Alignment, AlignmentError, AlignmentToken
from ebl.corpus.text import Line, ManuscriptLine, Text
from ebl.corpus.text_serializer import TextSerializer
from ebl.dictionary.word import WordId
from ebl.errors import DataError, Defect, NotFoundError
from ebl.fragment.transliteration import Transliteration
from ebl.fragment.value import INVALID_READING
from ebl.tests.factories.corpus import TextFactory
from ebl.text.labels import LineNumberLabel
from ebl.text.line import TextLine
from ebl.text.reconstructed_text import AkkadianWord, StringPart
from ebl.text.token import Word

COLLECTION = 'texts'
TEXT = TextFactory.build()
DEHYDRATED_TEXT = attr.evolve(TEXT, chapters=tuple(
    attr.evolve(chapter, manuscripts=tuple(
        attr.evolve(manuscript, references=tuple(
            attr.evolve(
                reference,
                document=None
            )
            for reference in manuscript.references
        ))
        for manuscript in chapter.manuscripts
    ))
    for chapter in TEXT.chapters
))
ANY_USER = Guest()


def to_dict(text: Text) -> dict:
    return TextSerializer.serialize(text, False)


def expect_bibliography(bibliography, when):
    for chapter in TEXT.chapters:
        for manuscript in chapter.manuscripts:
            for reference in manuscript.references:
                (when(bibliography)
                 .find(reference.id)
                 .thenReturn(reference.document))


def expect_validate_references(bibliography, when, text=TEXT):
    (pydash
     .chain(text.chapters)
     .flat_map(lambda chapter: chapter.manuscripts)
     .map(lambda manuscript: manuscript.references)
     .for_each(lambda references:
               when(bibliography).validate_references(references).thenReturn())
     .value())


def allow_validate_references(bibliography, when):
    when(bibliography).validate_references(...).thenReturn()


def expect_invalid_references(bibliography, when):
    when(bibliography).validate_references(...).thenRaise(DataError())


def expect_signs(sign_list, when, sign='X', text=TEXT):
    (pydash
     .chain(text.chapters)
     .flat_map(lambda chapter: chapter.lines)
     .flat_map(lambda line: line.manuscripts)
     .map(lambda manuscript: manuscript.line.atf)
     .map(lambda atf: Transliteration(atf).values)
     .for_each(lambda values: when(sign_list)
               .map_readings(values)
               .thenReturn([[sign]]))
     .value())


def expect_invalid_signs(sign_list, when):
    when(sign_list).map_readings(...).thenReturn([[INVALID_READING]])


def expect_text_update(bibliography, changelog, dehydrated_text,
                       dehydrated_updated_text, sign_list, text_repository,
                       user, when):
    expect_signs(sign_list, when, text=dehydrated_updated_text)
    expect_validate_references(bibliography, when, dehydrated_text)
    when(text_repository).find(TEXT.id).thenReturn(dehydrated_text)
    (when(text_repository)
     .update(TEXT.id, dehydrated_updated_text)
     .thenReturn(dehydrated_updated_text))
    when(changelog).create(
        COLLECTION,
        user.profile,
        {**to_dict(dehydrated_text), '_id': dehydrated_text.id},
        {**to_dict(dehydrated_updated_text), '_id': dehydrated_updated_text.id}
    ).thenReturn()


def test_creating_text(corpus,
                       text_repository,
                       bibliography,
                       changelog,
                       sign_list,
                       user,
                       when):
    expect_signs(sign_list, when)
    expect_validate_references(bibliography, when)
    when(changelog).create(
        COLLECTION,
        user.profile,
        {'_id': TEXT.id},
        {**to_dict(TEXT), '_id': TEXT.id}
    ).thenReturn()
    when(text_repository).create(TEXT).thenReturn()

    corpus.create(TEXT, user)


def test_create_raises_exception_if_invalid_signs(corpus,
                                                  bibliography,
                                                  sign_list,
                                                  when):
    allow_validate_references(bibliography, when)
    expect_invalid_signs(sign_list, when)

    with pytest.raises(DataError):
        corpus.create(TEXT, ANY_USER)


def test_create_raises_exception_if_invalid_references(corpus,
                                                       bibliography,
                                                       when):
    expect_invalid_references(bibliography, when)

    with pytest.raises(DataError):
        corpus.create(TEXT, ANY_USER)


def test_finding_text(corpus, text_repository, bibliography, when):
    when(text_repository).find(TEXT.id).thenReturn(DEHYDRATED_TEXT)
    expect_bibliography(bibliography, when)

    assert corpus.find(TEXT.id) == TEXT


def test_listing_texts(corpus, text_repository, when):
    when(text_repository).list().thenReturn([DEHYDRATED_TEXT])

    assert corpus.list() == [DEHYDRATED_TEXT]


def test_find_raises_exception_if_references_not_found(corpus,
                                                       text_repository,
                                                       bibliography,
                                                       when):
    when(text_repository).find(TEXT.id).thenReturn(DEHYDRATED_TEXT)
    when(bibliography).find(...).thenRaise(NotFoundError())

    with pytest.raises(Defect):
        corpus.find(TEXT.id)


def test_updating_alignment(corpus,
                            text_repository,
                            bibliography,
                            changelog,
                            sign_list,
                            user,
                            when):
    dehydrated_updated_text = attr.evolve(DEHYDRATED_TEXT, chapters=(
        attr.evolve(DEHYDRATED_TEXT.chapters[0], lines=(
            attr.evolve(DEHYDRATED_TEXT.chapters[0].lines[0], manuscripts=(
                attr.evolve(
                    DEHYDRATED_TEXT.chapters[0].lines[0].manuscripts[0],
                    line=TextLine('1.', (Word('ku]-nu-ši', alignment=0),))
                ),
            )),
        )),
    ))
    expect_text_update(bibliography, changelog, DEHYDRATED_TEXT,
                       dehydrated_updated_text, sign_list, text_repository,
                       user, when)

    alignment = Alignment((
        (
            (AlignmentToken('ku]-nu-ši', 0),),
        ),
    ))
    corpus.update_alignment(TEXT.id, 0, alignment, user)


@pytest.mark.parametrize('alignment', [
    Alignment((
            (
                    (AlignmentToken('ku]-nu-ši', 0),
                     AlignmentToken('ku]-nu-ši', 0),),
            ),
    )),
    Alignment((
            (
                    tuple(),
            ),
    )),
    Alignment((
            (
                    (AlignmentToken('ku]-nu-ši', 0),),
                    (AlignmentToken('ku]-nu-ši', 0),)
            ),
    )),
    Alignment((
            tuple()
    )),
    Alignment((
            (
                    (AlignmentToken('ku]-nu-ši', 0),),
            ),
            (
                    (AlignmentToken('ku]-nu-ši', 0),),
            )
    )),
    Alignment(tuple()),
    Alignment((
        (
            (AlignmentToken('invalid value', 0),),
        ),
    ))

])
def test_invalid_alignment(alignment,
                           corpus,
                           text_repository,
                           when):
    when(text_repository).find(TEXT.id).thenReturn(DEHYDRATED_TEXT)
    with pytest.raises(AlignmentError):
        corpus.update_alignment(TEXT.id, 0, alignment, ANY_USER)


def test_updating_manuscripts(corpus,
                              text_repository,
                              bibliography,
                              changelog,
                              sign_list,
                              user,
                              when):
    dehydrated_updated_text = attr.evolve(DEHYDRATED_TEXT, chapters=(
        attr.evolve(DEHYDRATED_TEXT.chapters[0], manuscripts=(
            attr.evolve(DEHYDRATED_TEXT.chapters[0].manuscripts[0],
                        notes='Updated manuscript.'),
        )),
    ))
    expect_text_update(bibliography, changelog, DEHYDRATED_TEXT,
                       dehydrated_updated_text, sign_list, text_repository,
                       user, when)

    manuscripts = (
        dehydrated_updated_text.chapters[0].manuscripts[0],
    )
    corpus.update_manuscripts(TEXT.id, 0, manuscripts, user)


@pytest.mark.parametrize('manuscripts', [
    tuple(),
    (
        DEHYDRATED_TEXT.chapters[0].manuscripts[0],
        DEHYDRATED_TEXT.chapters[0].manuscripts[0]
    )
])
def test_invalid_manuscripts(manuscripts,
                             corpus,
                             text_repository,
                             when):
    when(text_repository).find(TEXT.id).thenReturn(DEHYDRATED_TEXT)
    with pytest.raises(DataError):
        corpus.update_manuscripts(TEXT.id, 0, manuscripts, ANY_USER)


def test_update_manuscripts_raises_exception_if_invalid_references(
       corpus,
       text_repository,
       bibliography,
       when
):
    manuscripts = TEXT.chapters[0].manuscripts
    when(text_repository).find(TEXT.id).thenReturn(DEHYDRATED_TEXT)
    expect_invalid_references(bibliography, when)

    with pytest.raises(DataError):
        corpus.update_manuscripts(TEXT.id, 0, manuscripts, ANY_USER)


def test_updating_lines(corpus,
                        text_repository,
                        bibliography,
                        changelog,
                        sign_list,
                        user,
                        when):
    dehydrated_updated_text = attr.evolve(DEHYDRATED_TEXT, chapters=(
        attr.evolve(DEHYDRATED_TEXT.chapters[0], lines=(
            attr.evolve(DEHYDRATED_TEXT.chapters[0].lines[0],
                        number=LineNumberLabel.from_atf("1'.")),
        )),
    ))
    expect_text_update(bibliography, changelog, DEHYDRATED_TEXT,
                       dehydrated_updated_text, sign_list, text_repository,
                       user, when)

    lines = dehydrated_updated_text.chapters[0].lines
    corpus.update_lines(TEXT.id, 0, lines, user)


def test_merging_lines(corpus,
                       text_repository,
                       bibliography,
                       changelog,
                       sign_list,
                       user,
                       when):
    number = LineNumberLabel('1')
    reconstruction = (AkkadianWord((StringPart('buāru'),)),)
    text_line = TextLine('1.', (
        Word('kur',
             unique_lemma=(WordId('word1'),),
             alignment=0),
        Word('ra',
             unique_lemma=(WordId('word2'),),
             alignment=1)
    ))
    manuscript_id = DEHYDRATED_TEXT.chapters[0].manuscripts[0].id
    line = Line(number, reconstruction, (
        ManuscriptLine(manuscript_id,
                       tuple(),
                       text_line),
    ))
    new_text_line = TextLine('1.', (
        Word('kur'),
        Word('pa')
    ))
    new_line = Line(number, reconstruction, (
        ManuscriptLine(manuscript_id,
                       tuple(),
                       text_line.merge(new_text_line)),
    ))
    dehydrated_text = attr.evolve(DEHYDRATED_TEXT, chapters=(
        attr.evolve(DEHYDRATED_TEXT.chapters[0], lines=(line, )),
    ))
    dehydrated_updated_text = attr.evolve(DEHYDRATED_TEXT, chapters=(
        attr.evolve(DEHYDRATED_TEXT.chapters[0], lines=(new_line, )),
    ))
    expect_text_update(bibliography, changelog, dehydrated_text,
                       dehydrated_updated_text, sign_list, text_repository,
                       user, when)

    lines = (
        Line(number, reconstruction, (
            ManuscriptLine(
                manuscript_id,
                tuple(),
                new_text_line
            ),
        )),
    )
    corpus.update_lines(TEXT.id, 0, lines, user)


def test_update_lines_raises_exception_if_invalid_signs(
        corpus,
        text_repository,
        bibliography,
        sign_list,
        when
):
    lines = TEXT.chapters[0].lines
    when(text_repository).find(TEXT.id).thenReturn(DEHYDRATED_TEXT)
    allow_validate_references(bibliography, when)
    expect_invalid_signs(sign_list, when)

    with pytest.raises(DataError):
        corpus.update_lines(TEXT.id, 0, lines, ANY_USER)
