from dataclasses import dataclass, field as dcfield
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


@dataclass(kw_only=True)
class Type:
    name: str


@dataclass(kw_only=True)
class Field:
    name: str
    type: Type
    clsRef: "ClassRef"
    cls: "Class" = dcfield(init=False)

    def resolve_references(self, cls: "Class"):
        if cls.name != self.clsRef.name:
            raise ValueError(
                f"Class {cls.name} does not match reference {self.clsRef.name}"
            )
        self.cls = cls


@dataclass(kw_only=True)
class FieldRef:
    clsRef: "ClassRef"
    name: str
    cls: "Class" = dcfield(init=False)

    def resolve_references(self, cls: "Class") -> Field:
        if cls.name != self.clsRef.name:
            raise ValueError(
                f"Class {cls.name} does not match reference {self.clsRef.name}"
            )
        self.cls = cls
        return find_one(self.cls.fields, name=self.name)


@dataclass(kw_only=True)
class Literal:
    value: str | int | float


@dataclass(kw_only=True)
class FunctionCall:
    function: "Method" = dcfield(init=False)
    functionRef: "MethodRef"
    params: list[Literal]

    def resolve_references(self, classes: list["Class"]):
        self.function = self.functionRef.resolve_references(classes)
        self.function.resolve_references(classes)


Statement = FunctionCall


@dataclass(kw_only=True)
class Method:
    name: str
    clsRef: "ClassRef"
    cls: "Class" = dcfield(init=False)
    params: list[Any]
    returnType: Type
    body: list[Statement]

    def resolve_references(self, classes: list["Class"]):
        for cls in classes:
            if cls.name == self.clsRef.name:
                self.cls = cls
                break
        else:
            raise ValueError(f"Class {self.clsRef.name} not found")
        for statement in self.body:
            statement.resolve_references(classes)


@dataclass(kw_only=True)
class Class:
    name: str
    fields: list[Field]
    methods: list[Method]
    classes: list["Class"]

    def __post_init__(self):
        self.classes.append(self)
        for method in self.methods:
            method.resolve_references(self.classes)
        # for field in self.fields:
        #     field.resolve_references(self.classes)


@dataclass(kw_only=True)
class ClassRef:
    name: str


@dataclass(kw_only=True)
class MethodRef:
    clsRef: "ClassRef"
    name: str
    cls: "Class" = dcfield(init=False)

    def resolve_references(self, classes: list["Class"]) -> Method:
        for cls in classes:
            if cls.name == self.clsRef.name:
                self.cls = cls
                break
        else:
            raise ValueError(f"Class {self.clsRef.name} not found")
        return find_one(self.cls.methods, name=self.name)


@dataclass(kw_only=True)
class Program:
    classes: list[Class]
    pass


class ProgramProc:
    def __init__(self, program: program):
        self.program = program
        pass

    def reduce(self) -> Program:
        classes: list[Class] = []
        Class(
            classes=classes,
            name="System",
            fields=[],
            methods=[
                Method(
                    name="print",
                    params=[],
                    returnType=Type(name="result"),
                    clsRef=ClassRef(name="System"),
                    body=[],
                )
            ],
        )

        for block in self.program.blocks:
            cls: clazz | None = find_ancestor(block.block, clazz)
            if cls is not None:
                methods: list[Method] = []
                for content in cls.contents:
                    mthd: method | None = find_ancestor(content.content, method)
                    if mthd is not None:
                        statements: list[Statement] = []
                        for stmt in mthd.body.statements:
                            fcall: function_call | None = find_ancestor(
                                stmt.statement, function_call
                            )
                            if fcall is not None:
                                plist: list[Literal] = []
                                for param in fcall.params:
                                    lit: literal | None = find_ancestor(param, literal)
                                    if lit is not None:
                                        plist.append(
                                            Literal(
                                                value=lit.value,
                                            )
                                        )
                                statements.append(
                                    FunctionCall(
                                        functionRef=MethodRef(
                                            clsRef=ClassRef(name=fcall.class_name),
                                            name=fcall.method_name,
                                        ),
                                        params=plist,
                                    )
                                )
                        methods.append(
                            Method(
                                name=mthd.signature.name,
                                params=[],
                                returnType=Type(name="result"),
                                clsRef=ClassRef(name=cls.name),
                                body=statements,
                            )
                        )

                Class(
                    name=cls.name,
                    fields=[],
                    methods=methods,
                    classes=classes,
                )

        result = Program(classes=classes)
        return result


def reduce(program: program) -> Program:
    return ProgramProc(program).reduce()
