from textx import metamodel_from_str

grammar = r"""
program:
   blocks*= block
;
block:
    block =  class | block = interface
;
class:
    name=ID 'class' endl indent modifiers*=class_modifier contents*=class_content deindent
;

interface:
    name=ID 'interface' endl indent contents*=interface_content deindent
;

class_modifier:
    'implements' name=ID endl
;

class_content:
    content = field | method
;

interface_content:
    content = method_signature
;

field:
    'undefined'
;

method:
    signature=method_signature indent body=method_body deindent
;
method_signature:
    name=ID ('qry' | 'cmd' | 'prim') '(' ')' ':' returntype=primtype endl
;

method_body:
    statements+=statement
;
statement:
    'return' literal=literal endl
;
primtype:
    primtype = 'string'
;
literal:
    literal = STRING | NUMBER
;
endl:
    'NEWLINE'
;
indent:
    'INDENT'
;
deindent:
    'DEINDENT'
;

 """


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
            if char == "#":
                break
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
                temp.append(" INDENT ")
            else:
                temp.append(" DEINDENT ")
        result.append("".join(temp) + text)
    return " NEWLINE ".join(result)


def run():
    import os

    with open("lang.lang", "r") as f:
        initial_text = f.read()
        indented = indent(initial_text)
        print(indented)
        inlined = inline(indented)
        print(inlined)
        meta = metamodel_from_str(grammar)
        model = meta.model_from_str(inlined, debug=True)
        print(model)
        for block in model.blocks:
            print(block.block.name)
