from dataclasses import dataclass, field as dcfield
from .ast import *


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
class Expression:
    valueRef: Literal | FieldRef
    value: Literal | Field = dcfield(init=False)

    def resolve_references(self, cls: "Class"):
        self.value = (
            self.valueRef.resolve_references(cls)
            if issubclass(type(self.valueRef), FieldRef)
            else self.valueRef
        )
        if issubclass(type(self.value), Field):
            self.value.resolve_references(cls)


@dataclass(kw_only=True)
class ReturnStatement:
    value: Expression

    def resolve_references(self, cls: "Class"):
        self.value.resolve_references(cls)


@dataclass(kw_only=True)
class FunctionCall:
    function: "Method" = dcfield(init=False)
    functionRef: "MethodRef"
    params: list[Expression]

    def resolve_references(self, cls: "Class"):
        self.function = self.functionRef.resolve_references(cls)
        self.function.resolve_references(cls)


@dataclass(kw_only=True)
class Assignment:
    fieldRef: FieldRef
    field: Field = dcfield(init=False)
    value: Expression

    def resolve_references(self, cls: "Class"):
        self.field = self.fieldRef.resolve_references(cls)
        self.field.resolve_references(cls)
        self.value.resolve_references(cls)


Statement = ReturnStatement | FunctionCall | Assignment | Field


@dataclass(kw_only=True)
class Method:
    name: str
    clsRef: "ClassRef"
    cls: "Class" = dcfield(init=False)
    params: list[Field]
    returnType: Type
    body: list[Statement]

    def resolve_references(self, cls: "Class"):
        if cls.name != self.clsRef.name:
            raise ValueError(
                f"Method {self.name} belongs to class {self.clsRef.name}, not {cls.name}"
            )
        self.cls = cls
        for statement in self.body:
            statement.resolve_references(cls)


@dataclass(kw_only=True)
class Class:
    name: str
    fields: list[Field]
    methods: list[Method]

    def __post_init__(self):
        for method in self.methods:
            method.resolve_references(self)
        for field in self.fields:
            field.resolve_references(self)


@dataclass(kw_only=True)
class ClassRef:
    name: str


@dataclass(kw_only=True)
class MethodRef:
    clsRef: "ClassRef"
    name: str
    cls: "Class" = dcfield(init=False)

    def resolve_references(self, cls: "Class") -> Method:
        if cls.name != self.clsRef.name:
            raise ValueError(
                f"Class {cls.name} does not match reference {self.clsRef.name}"
            )
        self.cls = cls
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
        classes: list[Class] = [
            Class(
                name="System",
                fields=[],
                methods=[
                    Method(
                        name="print",
                        params=[
                            Field(
                                name="value",
                                type=Type(name="string"),
                                clsRef=ClassRef(name="System"),
                            )
                        ],
                        returnType=Type(name="result"),
                        clsRef=ClassRef(name="System"),
                        body=[],
                    )
                ],
            )
        ]
        types: list[Type] = [
            Type(name="string"),
            Type(name="result"),
        ]
        for block in self.program.blocks:
            if issubclass(type(block.block), clazz):
                cls: clazz = block.block
                fields: list[Field] = []
                methods: list[Method] = []
                for content in cls.contents:
                    if issubclass(type(content), field):
                        fld: field = content
                        fields.append(
                            Field(
                                name=fld.name,
                                type=find_one(types, name=fld.type.primtype),
                                clsRef=ClassRef(name=cls.name),
                            )
                        )
                    elif issubclass(type(content.content), method):
                        meth: method = content.content
                        body: list[Statement] = []
                        for statement in meth.body.statements:
                            if issubclass(type(statement.statement), return_stmt):
                                rt_stmt: return_stmt = statement.statement
                                if issubclass(type(rt_stmt.value), field_ref):
                                    f_ref: field_ref = rt_stmt.value
                                    body.append(
                                        ReturnStatement(
                                            value=Expression(
                                                valueRef=FieldRef(
                                                    clsRef=ClassRef(name=cls.name),
                                                    name=f_ref.field.name,
                                                )
                                            ),
                                        )
                                    )
                                elif issubclass(type(rt_stmt.value), literal):
                                    lit: literal = rt_stmt.value
                                    body.append(
                                        ReturnStatement(
                                            value=Expression(
                                                valueRef=Literal(value=lit.value)
                                            ),
                                        )
                                    )
                            elif issubclass(type(statement.statement), assignment):
                                assn: assignment = statement.statement
                                body.append(
                                    Assignment(
                                        fieldRef=FieldRef(
                                            clsRef=ClassRef(name=cls.name),
                                            name=assn.name,
                                        ),
                                        value=Expression(
                                            valueRef=Literal(value=assn.value)
                                        ),
                                    )
                                )
                            elif issubclass(type(statement.statement), function_call):
                                func_call: function_call = statement.statement
                                params: list[Expression] = []
                                for param in func_call.params:
                                    if issubclass(type(param), field_ref):
                                        f_ref: field_ref = param
                                        params.append(
                                            Expression(
                                                valueRef=FieldRef(
                                                    clsRef=ClassRef(name=cls.name),
                                                    name=f_ref.field.name,
                                                )
                                            )
                                        )
                                    elif issubclass(type(param), literal):
                                        lit: literal = param
                                        params.append(
                                            Expression(
                                                valueRef=Literal(value=lit.value)
                                            )
                                        )
                                body.append(
                                    FunctionCall(
                                        functionRef=MethodRef(
                                            clsRef=ClassRef(name=func_call.class_name),
                                            name=func_call.method_name,
                                        ),
                                        params=params,
                                    )
                                )
                            elif issubclass(type(statement.statement), field):
                                fld: field = statement.statement
                                fields.append(
                                    Field(
                                        name=fld.name,
                                        type=find_one(types, name=fld.type.primtype),
                                        clsRef=ClassRef(name=cls.name),
                                    )
                                )
                        methods.append(
                            Method(
                                name=meth.signature.name,
                                params=[
                                    Field(
                                        name=arg.name,
                                        type=find_one(types, name=arg.type.primtype),
                                        clsRef=ClassRef(name=cls.name),
                                    )
                                    for arg in meth.signature.params
                                ],
                                returnType=find_one(
                                    types, name=meth.signature.returntype.primtype
                                ),
                                clsRef=ClassRef(name=cls.name),
                                body=body,
                            )
                        )
                classes.append(
                    Class(
                        name=cls.name,
                        fields=fields,
                        methods=methods,
                    )
                )
        result = Program(classes=classes)
        return result


def reduce(program: program) -> Program:
    return ProgramProc(program).reduce()
