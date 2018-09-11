import re
import unicodedata


UNKNOWN_SIGN = 'X'


def clean_transliteration(transliteration):
    return [re.sub(r'(?<=\s)\(([^\(\)]+)\)', r'\1', line).strip()
            for line in
            (re.sub(r'\(\$_+\$\)|\?|\*|#|!|\$|%\w+\s+|(?<=\s)\s', '', line)
             for line in
             (re.sub(r'\s*{+\+?|}+({+\+?)?\s*|-|\.|\s+\|\s+', ' ', line)
              for line in
              (re.sub(r'^[^\.]+\.([^\.]+\.)?\s+|'
                      r'<<?\(?[^>]+\)?>?>|'
                      r'\[\(?|'
                      r'\)?\]|'
                      r'\.\.\.', '', line)
               for line in transliteration.split('\n') if
               line and
               not line.startswith('@') and
               not line.startswith('$') and
               not line.startswith('#') and
               not line.startswith('&') and
               not line.startswith('=:'))))]


def transliteration_to_signs(transliteration, sign_list):
    return [_parse_row(row, sign_list) for row in transliteration]


def _parse_row(row, sign_list):
    return [_parse_value(value, sign_list) for value in row.split(' ')]


def _parse_value(value, sign_list):
    match = re.fullmatch(r'\|?([.x%&+]?[A-ZṢŠṬ₀-₉]+)+\|?|'
                         r'\d+|'
                         r'[^\(]+\((.+)\)', value)
    if match:
        return match.group(2) or value
    else:
        return _parse_reading(value, sign_list)


def _parse_reading(reading, sign_list):
    match = re.fullmatch(r'([^₀-₉ₓ]+)([₀-₉ₓ]+)?', reading)
    if match:
        value = match.group(1)
        sub_index = match.group(2) or '1'
        normalized_sub_index = unicodedata.normalize('NFKC', sub_index)
        sign = sign_list.search(value, int(normalized_sub_index))
        return sign['_id'] if sign else UNKNOWN_SIGN
    else:
        return UNKNOWN_SIGN
