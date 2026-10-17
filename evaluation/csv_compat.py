"""Opt-in CSV quote compatibility, selected from syntax, never from GT values."""
import csv
import io


def backslash_to_standard(text):
    """Translate quoted-field \" and \\ escapes; preserve other backslashes.

    This is a lexical conversion only. The strict CSV reader still validates
    the result. Unquoted fields are never unescaped.
    """
    out = []
    state = 'start'
    escaped_quotes = 0
    i = 0
    while i < len(text):
        ch = text[i]
        if state == 'quoted':
            if ch == '\\' and i + 1 < len(text) and text[i + 1] in ('\\', '"'):
                following = text[i + 1]
                out.append('""' if following == '"' else '\\')
                escaped_quotes += following == '"'
                i += 2
                continue
            if ch == '"':
                state = 'closed'
        elif state == 'closed':
            if ch not in ',\r\n':
                raise csv.Error('Unexpected content after closing CSV quote')
            state = 'start'
        elif state == 'start':
            if ch == '"':
                state = 'quoted'
            elif ch not in ',\r\n':
                state = 'plain'
        elif ch in ',\r\n':
            state = 'start'
        out.append(ch)
        i += 1
    if state == 'quoted' or not escaped_quotes:
        raise csv.Error('Not a complete backslash-quoted CSV document')
    return ''.join(out)


def compatible_rows(text):
    """Standard CSV wins; fallback only for a strict CSV syntax error."""
    try:
        return list(csv.reader(io.StringIO(text, newline=''), strict=True)), 'standard'
    except csv.Error:
        converted = backslash_to_standard(text)
        return list(csv.reader(io.StringIO(converted, newline=''), strict=True)), 'backslash'
