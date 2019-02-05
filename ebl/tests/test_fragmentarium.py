# pylint: disable=R0913
import attr
from freezegun import freeze_time
import pytest
from ebl.errors import NotFoundError, DataError
from ebl.text.lemmatization import Lemmatization
from ebl.fragmentarium.transliteration import (
    Transliteration, TransliterationError
)
from ebl.text.token import Token, Word
from ebl.text.line import TextLine, ControlLine, EmptyLine
from ebl.text.text import Text


def test_create_and_find(fragmentarium, fragment):
    fragment_id = fragmentarium.create(fragment)

    assert fragmentarium.find(fragment_id) == fragment


def test_fragment_not_found(fragmentarium):
    with pytest.raises(NotFoundError):
        fragmentarium.find('unknown id')


@freeze_time("2018-09-07 15:41:24.032")
def test_update_transliteration(fragmentarium, transliterated_fragment, user):
    fragment_number = fragmentarium.create(transliterated_fragment)

    updated_fragment = fragmentarium.update_transliteration(
        fragment_number,
        Transliteration('1. x x\n2. x', 'updated notes'),
        user
    )
    db_fragment = fragmentarium.find(fragment_number)

    expected_fragment = transliterated_fragment.update_transliteration(
        Transliteration('1. x x\n2. x', 'updated notes', 'X X\nX'),
        user
    )

    assert updated_fragment == expected_fragment
    assert db_fragment == expected_fragment


def test_update_transliteration_invalid(fragmentarium, fragment, user):
    fragment_number = fragmentarium.create(fragment)

    with pytest.raises(TransliterationError):
        fragmentarium.update_transliteration(
            fragment_number,
            Transliteration('1. invalid values'),
            user
        )


@freeze_time("2018-09-07 15:41:24.032")
def test_transliteration_changelog(database,
                                   fragmentarium,
                                   fragment,
                                   user,
                                   make_changelog_entry):
    fragment_id = fragmentarium.create(fragment)
    fragmentarium.update_transliteration(
        fragment_id,
        Transliteration('1. x x x', 'updated notes'),
        user
    )

    expected_fragment = fragment.update_transliteration(
        Transliteration('1. x x x', 'updated notes', 'X X X'),
        user
    )

    expected_changelog = make_changelog_entry(
        'fragments',
        fragment_id,
        fragment.to_dict(),
        expected_fragment.to_dict()
    )
    assert database['changelog'].find_one(
        {'resource_id': fragment_id},
        {'_id': 0}
    ) == expected_changelog


def test_update_update_transliteration_not_found(fragmentarium, user):
    with pytest.raises(NotFoundError):
        fragmentarium.update_transliteration(
            'unknown.number',
            Transliteration('$ (the transliteration)', 'notes'),
            user
        )


@freeze_time("2018-09-07 15:41:24.032")
def test_update_lemmatization(fragmentarium,
                              transliterated_fragment,
                              user):
    fragment_number = fragmentarium.create(transliterated_fragment)
    tokens = transliterated_fragment.text.lemmatization.to_list()
    tokens[1][1]['uniqueLemma'] = ['aklu I']
    lemmatization = Lemmatization.from_list(tokens)

    updated_fragment = fragmentarium.update_lemmatization(
        fragment_number,
        lemmatization,
        user
    )
    db_fragment = fragmentarium.find(fragment_number)

    expected_fragment = transliterated_fragment.update_lemmatization(
        lemmatization
    )

    assert updated_fragment == expected_fragment
    assert db_fragment == expected_fragment


@freeze_time("2018-09-07 15:41:24.032")
def test_lemmatization_changelog(database,
                                 fragmentarium,
                                 transliterated_fragment,
                                 user,
                                 make_changelog_entry):
    fragment_number = fragmentarium.create(transliterated_fragment)
    tokens = transliterated_fragment.text.lemmatization.to_list()
    tokens[1][1]['uniqueLemma'] = ['aklu I']
    lemmatization = Lemmatization.from_list(tokens)
    fragmentarium.update_lemmatization(
        fragment_number,
        lemmatization,
        user
    )

    expected_fragment = transliterated_fragment.update_lemmatization(
        lemmatization
    )

    expected_changelog = make_changelog_entry(
        'fragments',
        fragment_number,
        transliterated_fragment.to_dict(),
        expected_fragment.to_dict()
    )
    assert database['changelog'].find_one(
        {'resource_id': fragment_number},
        {'_id': 0}
    ) == expected_changelog


def test_update_update_lemmatization_not_found(fragmentarium, user):
    with pytest.raises(NotFoundError):
        fragmentarium.update_lemmatization(
            'K.1',
            Lemmatization.from_list([[{'value': '1.', 'uniqueLemma': []}]]),
            user
        )


def test_statistics(fragmentarium, fragment):
    for test_fragment in [

            attr.evolve(fragment, number='1', text=Text((
                TextLine('1.', (Word('SU'), Word('line'))),
                ControlLine('$', (Token('ignore'), )),
                EmptyLine()
            ))),
            attr.evolve(fragment, number='2', text=Text((
                ControlLine('$', (Token('ignore'), )),
                TextLine('1.', (Word('SU'), )),
                TextLine('1.', (Word('SU'), )),
                ControlLine('$', (Token('ignore'), )),
                TextLine('1.', (Word('SU'), )),
            ))),
            attr.evolve(fragment, number='3', text=Text())
    ]:
        fragmentarium.create(test_fragment)

    assert fragmentarium.statistics() == {
        'transliteratedFragments': 2,
        'lines': 4
    }


def test_statistics_no_fragments(fragmentarium):
    assert fragmentarium.statistics() == {
        'transliteratedFragments': 0,
        'lines': 0
    }


def test_search_finds_by_id(fragmentarium,
                            fragment,
                            another_fragment):
    fragmentarium.create(fragment)
    fragmentarium.create(another_fragment)

    assert fragmentarium.search(fragment.number) == [fragment]


def test_search_finds_by_accession(fragmentarium,
                                   fragment,
                                   another_fragment):
    fragmentarium.create(fragment)
    fragmentarium.create(another_fragment)

    assert fragmentarium.search(fragment.accession) == [fragment]


def test_search_finds_by_cdli(fragmentarium,
                              fragment,
                              another_fragment):
    fragmentarium.create(fragment)
    fragmentarium.create(another_fragment)

    assert fragmentarium.search(fragment.cdli_number) == [fragment]


def test_search_not_found(fragmentarium):
    assert fragmentarium.search('K.1') == []


@pytest.mark.parametrize("transliteration,lines", [
    ('ana u₄', [
        ['2\'. [...] GI₆ ana u₄-š[u ...]']
    ]),
    ('ku', [
        ['1\'. [...-ku]-nu-ši [...]']
    ]),
    ('u₄', [
        ['2\'. [...] GI₆ ana u₄-š[u ...]'],
        ['6\'. [...] x mu ta-ma-tu₂']
    ]),
    ('GI₆ ana\nu ba ma', [
        [
            '2\'. [...] GI₆ ana u₄-š[u ...]',
            '3\'. [... k]i-du u ba-ma-t[i ...]'
        ]
    ]),
    ('ši tu₂', None),
])
def test_search_signs(transliteration,
                      lines,
                      sign_list,
                      signs,
                      fragmentarium,
                      transliterated_fragment,
                      another_fragment):
    fragmentarium.create(transliterated_fragment)
    fragmentarium.create(another_fragment)
    for sign in signs:
        sign_list.create(sign)

    result = fragmentarium.search_signs(
        Transliteration(transliteration)
    )
    expected = [
        attr.evolve(transliterated_fragment, matching_lines=lines)
    ] if lines else []

    assert result == expected


def test_find_lemmas(fragmentarium,
                     dictionary,
                     lemmatized_fragment,
                     word):
    matching_word = {
        **word,
        '_id': 'ginâ I'
    }
    fragmentarium.create(lemmatized_fragment)
    dictionary.create(word)
    dictionary.create(matching_word)

    assert fragmentarium.find_lemmas('GI₆') == [[matching_word]]


def test_update_references(fragmentarium,
                           fragment,
                           reference,
                           bibliography,
                           bibliography_entry,
                           user):
    bibliography.create(bibliography_entry, user)
    fragment_number = fragmentarium.create(fragment)
    references = (reference,)
    updated_fragment = fragmentarium.update_references(
        fragment_number,
        references,
        user
    )
    db_fragment = fragmentarium.find(fragment_number)
    expected_fragment = fragment.set_references(references)

    assert updated_fragment == expected_fragment
    assert db_fragment == expected_fragment


def test_update_references_invalid(fragmentarium, fragment, reference, user):
    fragment_number = fragmentarium.create(fragment)
    references = (reference,)

    with pytest.raises(DataError):
        fragmentarium.update_references(
            fragment_number,
            references,
            user
        )


@freeze_time("2018-09-07 15:41:24.032")
def test_references_changelog(database,
                              fragmentarium,
                              fragment,
                              reference,
                              bibliography,
                              bibliography_entry,
                              user,
                              make_changelog_entry):
    bibliography.create(bibliography_entry, user)
    fragment_number = fragmentarium.create(fragment)
    references = (reference,)
    fragmentarium.update_references(
        fragment_number,
        references,
        user
    )

    expected_fragment = fragment.set_references(references)

    expected_changelog = make_changelog_entry(
        'fragments',
        fragment_number,
        fragment.to_dict(),
        expected_fragment.to_dict()
    )
    assert database['changelog'].find_one(
        {'resource_id': fragment_number},
        {'_id': 0}
    ) == expected_changelog
