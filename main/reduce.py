from dataclasses import InitVar, dataclass, field as dcfield
from tkinter import NO
from .ast import *


def find_ancestor(cls: Any, ancestor: type) -> Any | None:
    match = ancestor.__name__ in {c.__name__ for c in type(cls).mro()}
    if match:
        return cls
    else:
        return None


def find_one(items, **query):
    result = next(
        (
            item
            for item in items
            if all(getattr(item, k) == v for k, v in query.items())
        ),
        None,
    )
    if result is None:
        raise ValueError(f"No item found with query {query}")
    return result


class Literal:
    value: str | int | float

    def __init__(self, value: str | int | float):
        self.value = value


class Method:
    name: str
    cls: "Class"
    params: list[Any]
    returnType: str
    body: list["Statement"]
    local_vars: list["LocalVar"]

    def __init__(self, cls: "Class", mthd: method):
        self.cls = cls
        self.name = mthd.signature.name
        self.returnType = mthd.signature.returntype.primtype
        self.body = []
        self.local_vars = []
        for stmt in mthd.body.statements:
            mcall: function_call | None = find_ancestor(stmt.statement, function_call)
            if mcall is not None:
                self.body += [MethodCall(self, mcall)]
            lvar: local_var | None = find_ancestor(stmt.statement, local_var)
            if lvar is not None:
                lv = LocalVar(self, lvar)
                self.body += [lv]
                self.local_vars += [lv]


class LocalVar:
    name: str
    type: str
    method: Method

    def __init__(self, method: Method, lvar: local_var):
        self.name = lvar.name
        self.type = lvar.type.primtype
        self.method = method


class Assignment:
    target: LocalVar
    method: Method
    value: Literal

    def __init__(self, method: Method, assmt: assignment):
        self.method = method
        for local_var in method.local_vars:
            if local_var.name == assmt.target:
                self.target = local_var
                break
        else:
            raise ValueError(
                f"No target found for assignment {assmt.target}={assmt.value.value}"
            )
        self.value = Literal(assmt.value.value)


class MethodCall:
    method: Method
    params: list[Literal]

    def __init__(self, method: Method, mcall: function_call):
        self.method = method
        self.params = [Literal(param.value) for param in mcall.params]


class Class:
    name: str

    methods: list[Method]
    program: "Program"

    def __init__(self, program: "Program", cls: clazz):
        self.methods = []
        self.name = cls.name
        self.program = program
        for content in cls.contents:
            mthd: method | None = find_ancestor(content.content, method)
            if mthd is not None:
                self.methods += [Method(self, mthd)]


Statement = MethodCall | LocalVar | Assignment


class Program:
    classes: list[Class]

    def __init__(self, pgm: program):
        self.classes = []
        for block in pgm.blocks:
            cls: clazz | None = find_ancestor(block.block, clazz)
            if cls is not None:
                self.classes += [Class(self, cls)]

    pass


def reduce(program: program) -> Program:
    result = Program(pgm=program)
    return result
