"""C/C++ comment extraction without mistaking literals for comments.

This is a lexical scanner, not a C++ parser. Unsupported translation-phase
constructs are rejected rather than silently misclassified.
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Comment:
    start: int
    end: int
    line: int
    end_line: int
    raw: str
    text: str


_RAW = re.compile(r'(?:u8|u|U|L)?R"([^\s()\\]{0,16})\(')
_QUOTED = re.compile(r'(?:u8|u|U|L)?["\']')
_TOKEN = re.compile(
    r"[A-Za-z_$][\w$]*|(?:\d[\w.']*|\.\d[\w.']*)|"
    r"<=>|>>=|<<=|->\*|\.\.\.|::|->|\+\+|--|&&|\|\||"
    r"<=|>=|==|!=|\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<|>>|##|\.\*|[^\s]"
)


def prose(raw):
    if raw.startswith("//"):
        return "\n".join(re.sub(r"^\s*//[/!]?[<]? ?", "", line)
                         for line in raw.splitlines()).strip()
    body = raw[2:-2]
    return "\n".join(re.sub(r"^\s*\* ?", "", line) for line in body.splitlines()).strip()


def scan(source):
    if "\\\n" in source or "\\\r\n" in source or "??/" in source:
        raise ValueError("Line splices and trigraphs are not supported by the C++ scanner")
    comments, tokens = [], []
    pos = 0
    while pos < len(source):
        if source[pos].isspace():
            pos += 1
            continue
        start = pos
        if source.startswith("//", pos):
            pos = source.find("\n", pos)
            if pos < 0:
                pos = len(source)
            raw = source[start:pos]
            comments.append(Comment(start, pos, source.count("\n", 0, start) + 1,
                                    source.count("\n", 0, pos) + 1, raw, prose(raw)))
            continue
        if source.startswith("/*", pos):
            stop = source.find("*/", pos + 2)
            if stop < 0:
                raise ValueError("Unterminated block comment")
            pos = stop + 2
            raw = source[start:pos]
            comments.append(Comment(start, pos, source.count("\n", 0, start) + 1,
                                    source.count("\n", 0, pos) + 1, raw, prose(raw)))
            continue
        raw_match = _RAW.match(source, pos)
        quoted = _QUOTED.match(source, pos)
        if raw_match:
            close = ")" + raw_match.group(1) + '"'
            stop = source.find(close, raw_match.end())
            if stop < 0:
                raise ValueError("Unterminated raw string")
            pos = stop + len(close)
        elif quoted:
            quote = source[quoted.end() - 1]
            pos = quoted.end()
            while pos < len(source):
                if source[pos] == "\\":
                    pos += 2
                elif source[pos] == quote:
                    pos += 1
                    break
                else:
                    pos += 1
            else:
                raise ValueError("Unterminated string or character literal")
        else:
            match = _TOKEN.match(source, pos)
            pos = match.end()
        tokens.append(source[start:pos])

    grouped = []
    for comment in comments:
        if grouped:
            prev = grouped[-1]
            between = source[prev.end:comment.start]
            # Join only adjacent standalone line comments, not trailing comments.
            standalone = not source[source.rfind("\n", 0, prev.start) + 1:prev.start].strip()
            if (prev.raw.startswith("//") and comment.raw.startswith("//") and
                    standalone and between.count("\n") == 1 and not between.strip()):
                raw = source[prev.start:comment.end]
                grouped[-1] = Comment(prev.start, comment.end, prev.line, comment.end_line,
                                      raw, prose(raw))
                continue
        grouped.append(comment)
    return grouped, tokens


def render_comment(text, original, indent=""):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Generator returned an empty comment")
    if "*/" in text or "\\\n" in text or text.rstrip().endswith("\\"):
        raise ValueError("Generator returned an unsafe comment delimiter or line splice")
    if text.lstrip().startswith(("//", "/*", "```")):
        raise ValueError("Generator must return prose without comment delimiters or fences")
    lines = text.strip().splitlines()
    if original.startswith("//"):
        marker = "///" if original.startswith("///") else "//"
        return ("\n" + indent).join(marker + (" " + line if line else "") for line in lines)
    return "/* " + ("\n" + indent + " * ").join(lines) + " */"


def assert_code_preserved(before, after):
    """Preserve tokens and significant preprocessor whitespace."""
    old_comments, old_tokens = scan(before)
    new_comments, new_tokens = scan(after)
    if old_tokens != new_tokens:
        raise ValueError("Executable tokens changed")

    def directives(source, comments):
        for comment in reversed(comments):
            # Comments are whitespace during preprocessing. Retain line breaks
            # so edits cannot silently move code into or out of a directive.
            blank = " " + "\n" * comment.raw.count("\n")
            source = source[:comment.start] + blank + source[comment.end:]
        return [line.strip() for line in source.splitlines() if line.lstrip().startswith("#")]

    if directives(before, old_comments) != directives(after, new_comments):
        raise ValueError("Preprocessor directive text or spacing changed")
