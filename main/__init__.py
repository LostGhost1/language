from ast import TypeVar
from textx import metamodel_from_file  # type: ignore
from .preprocessor import indent, inline

from .ast import classlist
from .reduce import *


def run_program(program: Program):
    main: Method | None = None
    flag = False
    for cls in program.classes:
        if cls.name == "Program":
            for method in cls.methods:
                if method.name == "Main":
                    main = method
                    flag = True
                    break
            if flag:
                break
    if main is None:
        raise ValueError("Program.Main not found")
    vars: dict[LocalVar, Literal | None] = {var: None for var in main.local_vars}
    for statement in main.body:
        mcall: MethodCall | None = find_ancestor(statement, MethodCall)
        if mcall is not None:
            if mcall.dst.cls.name == "System":
                if mcall.dst.name == "print":
                    # lit: Literal | None = find_ancestor(mcall.params[0], Literal)
                    # if lit is not None:
                    #     p = lit.value
                    # else:
                    #     lvar: LocalVar | None = find_ancestor(mcall.params[0], LocalVar)
                    #     if lvar is not None and lvar in vars and vars[lvar] is not None:
                    #         p = vars[lvar].value  # type: ignore
                    #     else:
                    #         raise ValueError("Variable not found")
                    print(mcall.params[0])
        assignment: Assignment | None = find_ancestor(statement, Assignment)
        if assignment is not None:
            vars[assignment.target] = assignment.value


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
