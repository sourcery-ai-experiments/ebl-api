import pytest

from ebl.fragment.transliteration import Transliteration
from ebl.text.atf import Atf


def test_ignored_lines():
    transliteration = Transliteration(Atf(
        '&K11111\n'
        '@reverse\n'
        '\n'
        '$ end of side\n'
        '$single ruling\n'
        '$ single ruling\n'
        '$double ruling\n'
        '$ double ruling\n'
        '$triple ruling\n'
        '$ triple ruling\n'
        '$ (random text)\n'
        '#note\n=: foo'
    ))
    assert transliteration.cleaned == []


def test_strip_line_numbers():
    transliteration = Transliteration(Atf(
        '1. mu\n2\'. me\na+1. e\n1.2. a\n3. kur. ra'
    ))
    assert transliteration.cleaned == [
        'mu',
        'me',
        'e',
        'a',
        'kur ra'
    ]


def test_map_spaces():
    transliteration = Transliteration(Atf(
        '1. šu-mu gid₂-ba\n'
        '2. {giš}BI.IS\n'
        '3. {giš}|BI.IS|\n'
        '4. {m}{d}\n'
        '5. {+tu-um}\n'
        '6. tu | na\n'
        '6. nibru{ki} | na\n'
        '6. nibru{{ki}} | na\n'
        '6. mu | {giš}BI\n'
        '6. mu | {{giš}}BI\n'
        '6. tu & na\n'
        '6. tu &2 na\n'
        '7. & e\n'
        '7. e &\n'
        '7. | e\n'
        '7. e |\n'
        '8. mu {{giš}}BI\n'
        '9. din-{d}x\n'
        '10. šu+mu\n'
        '11. {d}+a'
    ))

    assert transliteration.cleaned == [
        'šu mu gid₂ ba',
        'giš bi is',
        'giš |BI.IS|',
        'm d',
        'tu um',
        'tu na',
        'nibru ki na',
        'nibru ki na',
        'mu giš bi',
        'mu giš bi',
        'tu na',
        'tu na',
        'e',
        'e',
        'e',
        'e',
        'mu giš bi',
        'din d x',
        'šu mu',
        'd a'
    ]


def test_strip_lacuna():
    transliteration = Transliteration(Atf(
        '1. [... N]U KU₃\n'
        '2. [... a]-ba-an\n'
        '3. [...] ši [...]\n'
        '5. [(... a)]-ba\n'
        '6. [x (x) x]\n'
        '7. [(x) (x)]\n'
        '8. [(...)]\n'
        '9. ⸢ba⸣'
    ))
    assert transliteration.cleaned == [
        'nu ku₃',
        'a ba an',
        'ši',
        'a ba',
        'x x x',
        'x x',
        '',
        'ba'
    ]


def test_indent():
    transliteration = Transliteration(Atf('1. ($___$) ša₂'))
    assert transliteration.cleaned == [
        'ša₂'
    ]


def test_strip_flags():
    transliteration =\
        Transliteration(Atf('1.  ba! ba? ba# ba*\n2. $KU'))
    assert transliteration.cleaned == [
        'ba ba ba ba',
        'ku'
    ]


def test_strip_shifts():
    transliteration =\
        Transliteration(Atf('1. %es qa\n2. ba %g ba'))
    assert transliteration.cleaned == [
        'qa',
        'ba ba'
    ]


def test_strip_omissions():
    transliteration = Transliteration(Atf(
        '1.  <NU> KU₃\n2. <(ba)> an\n5. <<a>> ba'
    ))
    assert transliteration.cleaned == [
        'ku₃',
        'an',
        'ba'
    ]


def test_min():
    transliteration =\
        Transliteration(Atf('3. MIN<(an)> ši'))
    assert transliteration.cleaned == [
        'min ši'
    ]


def test_numbers():
    transliteration =\
        Transliteration(Atf('1. 1(AŠ)\n2. 1 2 10 20 30\n3. 256'))
    assert transliteration.cleaned == [
        '1(AŠ)',
        '1 2 10 20 30',
        '256'
    ]


def test_graphemes():
    graphemes = [
        '|BIxIS|',
        '|BI×IS|',
        '|BI.IS|',
        '|BI+IS|',
        '|BI&IS|',
        '|BI%IS|',
        '|BI@IS|',
        '|3×BI|',
        '|3xBI|',
        '|GEŠTU~axŠE~a@t|',
        '|(GI&GI)×ŠE₃|',
        '|UD.AB@g|'
    ]

    transliteration = Transliteration(Atf('\n'.join([
        f'{index}. {grapheme}'
        for index, grapheme in enumerate(graphemes)
    ])))

    assert transliteration.cleaned == graphemes


def test_lower_case():
    transliteration = Transliteration(Atf(
        '1. gid₂\n'
        '2. ši\n'
        '3. BI\n'
        '4. BI.IS\n'
        '4. BI+IS\n'
        '5. |BI.IS|\n'
        '6. DIŠ\n'
        '7. KU₃\n'
        '8. ku(KU₃)\n'
        '9. ku/|BI×IS|'
    ))

    assert transliteration.cleaned == [
        'gid₂',
        'ši',
        'bi',
        'bi is',
        'bi is',
        '|BI.IS|',
        'diš',
        'ku₃',
        'ku(KU₃)',
        'ku/|BI×IS|'
    ]


def test_strip_at():
    transliteration = Transliteration(Atf(
        '1. lu₂@v\n'
        '2. LU₂@v\n'
        '3. TA@v'
    ))

    assert transliteration.cleaned == [
        'lu₂',
        'lu₂',
        'ta'
    ]


def test_strip_line_continuation():
    transliteration = Transliteration(Atf(
        '1. ku →'
    ))

    assert transliteration.cleaned == [
        'ku'
    ]


@pytest.mark.parametrize('erasure,cleaned', [
    ('1. °\\° ku', 'ku'),
    ('°\\°  ku', 'ku'),
    ('1. °ra (ra) 1(AŠ) <(ra)> [(ra)]\\° ku', 'ku'),
    ('1. °<(1(AŠ))>\\° 2(DIŠ)', '2(DIŠ)'),
    ('1. °[(1(AŠ))]\\° 2(DIŠ)', '2(DIŠ)'),
    ('1. °\\ra° ku', 'ra ku'),
    ('1. °ra\\ku°', 'ku'),
    ('1. °\\KU°', 'ku')
])
def test_strip_erasure(erasure, cleaned):
    transliteration = Transliteration(Atf(erasure))

    assert transliteration.cleaned == [cleaned]
