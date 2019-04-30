from typing import Tuple

import pytest

from ebl.corpus.text import (Chapter, Classification, Manuscript,
                             ManuscriptType, Period, PeriodModifier,
                             Provenance, Stage, Text, TextId, Line,
                             ManuscriptLine)
from ebl.tests.factories.bibliography import ReferenceFactory
from ebl.text.atf import Surface
from ebl.text.labels import SurfaceLabel, ColumnLabel, Label, LineNumberLabel
from ebl.text.line import TextLine
from ebl.text.token import Word

CATEGORY = 1
INDEX = 2
NAME = 'Palm & Vine'
VERSES = 100
APPROXIMATE = True
CLASSIFICATION = Classification.ANCIENT
STAGE = Stage.NEO_BABYLONIAN
VERSION = 'A'
CHAPTER_NAME = 'IIc'
ORDER = 1
MANUSCRIPT_ID = 9001
SIGLUM_DISAMBIGUATOR = '1c'
MUSEUM_NUMBER = 'BM.x'
ACCESSION = ''
PERIOD_MODIFIER = PeriodModifier.LATE
PERIOD = Period.OLD_BABYLONIAN
PROVENANCE = Provenance.NINEVEH
TYPE = ManuscriptType.LIBRARY
NOTES = 'some notes'
REFERENCES = (ReferenceFactory.build(), )
LINE_NUMBER = '1.'
LINE_RECONSTRUCTION = 'idealized text'
LABELS = (SurfaceLabel.from_label(Surface.OBVERSE), )
MANUSCRIPT_TEXT = TextLine('1.', (Word('-ku]-nu-ši'),))


TEXT = Text(CATEGORY, INDEX, NAME, VERSES, APPROXIMATE, (
    Chapter(CLASSIFICATION, STAGE, VERSION, CHAPTER_NAME, ORDER, (
        Manuscript(
            MANUSCRIPT_ID,
            SIGLUM_DISAMBIGUATOR,
            MUSEUM_NUMBER,
            ACCESSION,
            PERIOD_MODIFIER,
            PERIOD,
            PROVENANCE,
            TYPE,
            NOTES,
            REFERENCES
        ),
    ), (
        Line(LINE_NUMBER, LINE_RECONSTRUCTION, (
            ManuscriptLine(MANUSCRIPT_ID, LABELS, MANUSCRIPT_TEXT),
        )),
    )),
))


def test_constructor_sets_correct_fields():
    assert TEXT.id == TextId(CATEGORY, INDEX)
    assert TEXT.category == CATEGORY
    assert TEXT.index == INDEX
    assert TEXT.name == NAME
    assert TEXT.number_of_verses == VERSES
    assert TEXT.approximate_verses == APPROXIMATE
    assert TEXT.chapters[0].classification == CLASSIFICATION
    assert TEXT.chapters[0].stage == STAGE
    assert TEXT.chapters[0].version == VERSION
    assert TEXT.chapters[0].name == CHAPTER_NAME
    assert TEXT.chapters[0].order == ORDER
    assert TEXT.chapters[0].manuscripts[0].id == MANUSCRIPT_ID
    assert TEXT.chapters[0].manuscripts[0].siglum == (
        PROVENANCE,
        PERIOD,
        TYPE,
        SIGLUM_DISAMBIGUATOR
    )
    assert TEXT.chapters[0].manuscripts[0].siglum_disambiguator ==\
        SIGLUM_DISAMBIGUATOR
    assert TEXT.chapters[0].manuscripts[0].museum_number == MUSEUM_NUMBER
    assert TEXT.chapters[0].manuscripts[0].accession == ACCESSION
    assert TEXT.chapters[0].manuscripts[0].period_modifier == PERIOD_MODIFIER
    assert TEXT.chapters[0].manuscripts[0].period == PERIOD
    assert TEXT.chapters[0].manuscripts[0].provenance == PROVENANCE
    assert TEXT.chapters[0].manuscripts[0].type == TYPE
    assert TEXT.chapters[0].manuscripts[0].notes == NOTES
    assert TEXT.chapters[0].manuscripts[0].references == REFERENCES
    assert TEXT.chapters[0].lines[0].number == LINE_NUMBER
    assert TEXT.chapters[0].lines[0].reconstruction == LINE_RECONSTRUCTION
    assert TEXT.chapters[0].lines[0].manuscripts[0].manuscript_id ==\
        MANUSCRIPT_ID
    assert TEXT.chapters[0].lines[0].manuscripts[0].labels == LABELS
    assert TEXT.chapters[0].lines[0].manuscripts[0].line == MANUSCRIPT_TEXT


def test_giving_museum_number_and_accession_is_invalid():
    with pytest.raises(ValueError):
        Manuscript(
            MANUSCRIPT_ID,
            museum_number='when museum number if given',
            accession='then accession not allowed'
        )


@pytest.mark.parametrize('number', [
    '', '.', '1', '12', ' .', '. ', '1 .', ' 1.', '1. '
])
def test_not_atf_line_number_is_invalid(number):
    with pytest.raises(ValueError):
        Line(number)


def test_duplicate_ids_are_invalid():
    with pytest.raises(ValueError):
        Chapter(manuscripts=(
            Manuscript(
                MANUSCRIPT_ID,
                siglum_disambiguator='a',
            ),
            Manuscript(
                MANUSCRIPT_ID,
                siglum_disambiguator='b',
            ),
        ))


def test_duplicate_sigla_are_invalid():
    with pytest.raises(ValueError):
        Chapter(manuscripts=(
            Manuscript(
                MANUSCRIPT_ID,
                siglum_disambiguator=SIGLUM_DISAMBIGUATOR,
                period=PERIOD,
                provenance=PROVENANCE,
                type=TYPE
            ),
            Manuscript(
                MANUSCRIPT_ID + 1,
                siglum_disambiguator=SIGLUM_DISAMBIGUATOR,
                period=PERIOD,
                provenance=PROVENANCE,
                type=TYPE
            ),
        ))


@pytest.mark.parametrize('labels', [
    (ColumnLabel.from_label('i'),
     ColumnLabel.from_label('ii')),
    (SurfaceLabel.from_label(Surface.OBVERSE),
     SurfaceLabel.from_label(Surface.REVERSE)),
    (ColumnLabel.from_label('i'),
     SurfaceLabel.from_label(Surface.REVERSE)),
    (LineNumberLabel('1'),)
])
def test_invalid_labels(labels: Tuple[Label, ...]):
    with pytest.raises(ValueError):
        ManuscriptLine(
            manuscript_id=1,
            labels=labels,
            line=TextLine()
        )


def test_serializing_to_dict():
    # pylint: disable=E1101
    assert TEXT.to_dict() == {
        'category': CATEGORY,
        'index': INDEX,
        'name': NAME,
        'numberOfVerses': VERSES,
        'approximateVerses': APPROXIMATE,
        'chapters': [
            {
                'classification': CLASSIFICATION.value,
                'stage': STAGE.value,
                'version': VERSION,
                'name': CHAPTER_NAME,
                'order': ORDER,
                'manuscripts': [
                    {
                        'id': MANUSCRIPT_ID,
                        'siglumDisambiguator': SIGLUM_DISAMBIGUATOR,
                        'museumNumber': MUSEUM_NUMBER,
                        'accession': ACCESSION,
                        'periodModifier': PERIOD_MODIFIER.value,
                        'period': PERIOD.value,
                        'provenance': PROVENANCE.long_name,
                        'type': TYPE.long_name,
                        'notes': NOTES,
                        'references': [
                            reference.to_dict()
                            for reference in REFERENCES
                        ]
                    }
                ],
                'lines': [
                    {
                        'number': LINE_NUMBER,
                        'reconstruction': LINE_RECONSTRUCTION,
                        'manuscripts': [{
                            'manuscriptId': MANUSCRIPT_ID,
                            'labels': [label.to_value() for label in LABELS],
                            'line': MANUSCRIPT_TEXT.to_dict()
                        }]
                    }
                ]
            }
        ]
    }


def test_serializing_to_dict_with_documents():
    # pylint: disable=E1101
    assert TEXT.to_dict(True) == {
        'category': CATEGORY,
        'index': INDEX,
        'name': NAME,
        'numberOfVerses': VERSES,
        'approximateVerses': APPROXIMATE,
        'chapters': [
            {
                'classification': CLASSIFICATION.value,
                'stage': STAGE.value,
                'version': VERSION,
                'name': CHAPTER_NAME,
                'order': ORDER,
                'manuscripts': [
                    {
                        'id': MANUSCRIPT_ID,
                        'siglumDisambiguator': SIGLUM_DISAMBIGUATOR,
                        'museumNumber': MUSEUM_NUMBER,
                        'accession': ACCESSION,
                        'periodModifier': PERIOD_MODIFIER.value,
                        'period': PERIOD.value,
                        'provenance': PROVENANCE.long_name,
                        'type': TYPE.long_name,
                        'notes': NOTES,
                        'references': [
                            reference.to_dict(True)
                            for reference in REFERENCES
                        ]
                    }
                ],
                'lines': [
                    {
                        'number': LINE_NUMBER,
                        'reconstruction': LINE_RECONSTRUCTION,
                        'manuscripts': [{
                            'manuscriptId': MANUSCRIPT_ID,
                            'labels': [label.to_value() for label in LABELS],
                            'line': MANUSCRIPT_TEXT.to_dict()
                        }]
                    }
                ]
            }
        ]
    }


def test_stage():
    periods = [period.value for period in Period]
    stages = [stage.value for stage in Stage]
    assert stages == [*periods, 'Standard Babylonian']
