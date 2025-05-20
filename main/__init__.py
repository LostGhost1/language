from textx import metamodel_from_file
from .preprocessor import indent, inline

from .ast import classlist
from .reduce import Program, reduce


def is_subclass(cls, class_name):
    return class_name.__name__ in {c.__name__ for c in cls.mro()}


def run_program(program: Program):
    print(program)


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
