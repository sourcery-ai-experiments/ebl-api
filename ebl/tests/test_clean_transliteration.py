from ebl.fragmentarium.transliteration_to_signs import clean_transliteration


def test_ignored_lines():
    transliteration = '&K11111\n@reverse\n\n$ end of side\n#note\n=: foo'
    assert clean_transliteration(transliteration) == []


def test_strip_line_numbers():
    transliteration = '1. mu\n2\'. me\na+1. e\n1.2. a'
    assert clean_transliteration(transliteration) == [
        'mu',
        'me',
        'e',
        'a'
    ]


def test_map_spaces():
    transliteration = ('1. šu-mu gid₂-ba\n'
                       '2. {giš}BI.IS\n'
                       '3. {m}{d}\n'
                       '4. {+tu-um}\n'
                       '5. tu | na\n'
                       '6. |BIxIS|\n'
                       '7. mu {{giš}}BI')

    assert clean_transliteration(transliteration) == [
        'šu mu gid₂ ba',
        'giš BI IS',
        'm d',
        'tu um',
        'tu na',
        '|BIxIS|',
        'mu giš BI'
    ]


def test_strip_lacuna():
    transliteration =\
        '1.  [... N]U KU₃\n2. [... a]-ba-an\n3. [...] ši [...]\n5. [(... a)]-ba'
    assert clean_transliteration(transliteration) == [
        'NU KU₃',
        'a ba an',
        'ši',
        'a ba'
    ]


def test_indent():
    transliteration = '1. ($___$) ša₂'
    assert clean_transliteration(transliteration) == [
        'ša₂'
    ]

def test_strip_flags():
    transliteration =\
        '1.  ba! ba? ba# ba*\n2. $KU'
    assert clean_transliteration(transliteration) == [
        'ba ba ba ba',
        'KU'
    ]

def test_strip_shifts():
    transliteration =\
        '1. %es qa\n2. ba %g ba'
    assert clean_transliteration(transliteration) == [
        'qa',
        'ba ba'
    ]


def test_strip_omissions():
    transliteration =\
        '1.  <NU> KU₃\n2. <(ba)> an\n3. MIN<(an)> ši\n5. <<a>> ba'
    assert clean_transliteration(transliteration) == [
        'KU₃',
        'an',
        'ši',
        'ba'
    ]
