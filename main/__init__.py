from ast import TypeVar
from typing import Any, Generic, Type
from textx import metamodel_from_file
from .preprocessor import indent, inline

from .ast import classlist
from .reduce import Program, reduce

T = TypeVar("T")


def run_program(program: Program):
    for cls in program.classes:
        if cls.name == "Program":
            for method in cls.methods:
                if method.name == "Main":
                    for statement in method.body:
                        if statement.function.cls.name == "System":
                            if statement.function.name == "print":
                                print(
                                    ", ".join([str(x.value) for x in statement.params])
                                )


def run():
    import os

    with open("lang.lang", "r") as f:
        initial_text = f.read()
        indented = indent(initial_text)
        print(indented)
        inlined = inline(indented)
        print(inlined)

        meta = metamodel_from_file("grammar.tx", classes=classlist)
        program: Program = reduce(meta.model_from_str(inlined))  # type: ignore
        run_program(program)
