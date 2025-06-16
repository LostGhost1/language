from ast import TypeVar
from textx import metamodel_from_file

from main.reduce import Expression, Literal, LocalVar, MethodCall  # type: ignore
from .preprocessor import indent, inline

from .ast import classlist
from .reduce import *


def resolve(
    method: Method, vars: dict[LocalVar, Literal | None], expr: Expression
) -> Literal:
    lit: Literal | None = find_ancestor(expr.value, Literal)
    if lit is not None:
        return lit
    lvar: LocalVar | None = find_ancestor(expr.value, LocalVar)
    if lvar is not None:
        result = vars[lvar]
        if result is not None:
            return result
        raise ValueError("Variable not found")
    mc: MethodCall | None = find_ancestor(expr.value, MethodCall)
    if mc is not None:
        return mcall(
            method.cls.program,
            {
                mc.dst.params[i]: resolve(method, vars, p)
                for i, p in enumerate(mc.params)
            },
            mc.dst,
        )
    raise ValueError("Expression not resolved")
    pass


def mcall(program: Program, params: dict[Param, Literal], method: Method) -> Literal:
    vars: dict[LocalVar, Literal | None] = {var: None for var in method.local_vars}
    for statement in method.body:
        mcall: MethodCall | None = find_ancestor(statement, MethodCall)
        if mcall is not None:
            if mcall.dst.cls.name == "System":
                if mcall.dst.name == "print":
                    lit: Literal | None = find_ancestor(mcall.params[0].value, Literal)
                    if lit is not None:
                        p = lit.value
                    else:
                        lvar: LocalVar | None = find_ancestor(
                            mcall.params[0].value, LocalVar
                        )
                        if lvar is not None and lvar in vars and vars[lvar] is not None:
                            p = vars[lvar].value  # type: ignore
                        else:
                            raise ValueError("Variable not found")
                    print(p)
        assignment: Assignment | None = find_ancestor(statement, Assignment)
        if assignment is not None:
            vars[assignment.target] = resolve(method, vars, assignment.value)
        return_stmt: Return | None = find_ancestor(statement, Return)
        if return_stmt is not None:
            return resolve(method, vars, return_stmt.value)
    raise ValueError("MethodCall not resolved")


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
    result = mcall(program, {}, main)
    if result.value == "ok":
        print("Program executed successfully")
    else:
        print(f"Program failed")


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
