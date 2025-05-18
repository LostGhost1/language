from parsimonious import Grammar

grammar = Grammar(
    r"""
    grammar = block*
    block = name whitespace block_type endl indent block_body deindent
    block_type = "interface" / "class"
    block_body = block_modifier* block_content*
    block_content = name whitespace big_type signature endl body?
    big_type = "qry"
    signature = "()" whitespace ":" whitespace type
    body = indent body_content deindent
    body_content = statement+
    statement = "return" whitespace literal endl
    literal = ~"\"[A-Za-z0-9]*\""
    type = "string"
    block_modifier = implements_interface
    implements_interface = "implements" whitespace name endl
    whitespace = ~"[' ']*"
    name = ~"[A-Z0-9]*"i
    endl = "_NEWLINE_"
    indent = "_INDENT_"
    deindent = "_DEINDENT_"
    """
)


class Indent:
    pass


class DeIndent:
    pass


def indent(text: str) -> list[tuple[list[Indent | DeIndent], str]]:
    prev_indent = 0
    result: list[tuple[list[Indent | DeIndent], str]] = []
    for line in text.split("\n"):
        state = "count"
        current_indent = 0
        temp_indents: list[Indent | DeIndent] = []
        temp_str = [""]
        for char in line:
            if state == "count" and (char == "\t" or char == " "):
                current_indent += 1 if char == " " else 4
            elif state == "count" and (char != "\t" and char != " "):
                temp_indents = (
                    [Indent() for _ in range((current_indent - prev_indent) // 4)]
                    if current_indent > prev_indent
                    else [
                        DeIndent() for _ in range((prev_indent - current_indent) // 4)
                    ]
                )
                prev_indent = current_indent
                state = "consume"
                temp_str.append(char)
            elif state == "consume":
                temp_str.append(char)
            else:
                raise ValueError("Invalid state")
        if len(temp_str) != 1 or len(temp_indents) != 0:
            result.append((temp_indents, "".join(temp_str)))
    result.append(([DeIndent() for _ in range((prev_indent - 0) // 4)], ""))
    return result


def inline(indented: list[tuple[list[Indent | DeIndent], str]]) -> str:
    result = []
    for indents, text in indented:
        temp = []
        for indent in indents:
            if isinstance(indent, Indent):
                temp.append("_INDENT_")
            else:
                temp.append("_DEINDENT_")
        result.append("".join(temp) + text)
    return "_NEWLINE_".join(result)


def run():
    import os

    with open("lang.lang", "r") as f:
        initial_text = f.read()
        indented = indent(initial_text)
        print(indented)
        inlined = inline(indented)
        print(inlined)
        try:
            parsed = grammar.match(inlined)
        except Exception as e:
            print(e)
            raise
        print(parsed)
