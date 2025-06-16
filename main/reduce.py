from enum import Enum, StrEnum, auto
from .ast import *


def find_ancestor(cls: Any, ancestor: type) -> Any | None:
    match = ancestor.__name__ in {c.__name__ for c in type(cls).mro()}
    if match:
        return cls
    else:
        return None


class Result(StrEnum):
    OK = auto()
    ERROR = auto()
    PENDING = auto()


class Type:
    type: "type"

    def __init__(self, t: primtype):
        if t.primtype == "string":
            self.type = str
        elif t.primtype == "int":
            self.type = int
        elif t.primtype == "float":
            self.type = float
        elif t.primtype == "result":
            self.type = Result
        else:
            raise ValueError("Invalid type")


class Literal:
    value: str | int | float | Result
    type: "Type"

    @classmethod
    def from_literal(cls, value: literal):
        self = cls()
        if (
            value.value_str != ""
            and (value.value_num == 0.0 or value.value_num == 0)
            and value.value_result == ""
        ):
            self.value = value.value_str
            self.type = Type(primtype(primtype="string", parent=None))  # type: ignore
        elif (
            (value.value_num != 0.0 or value.value_num != 0)
            and value.value_result == ""
            and value.value_str == ""
        ):
            self.value = value.value_num
            self.type = Type(primtype(primtype="int", parent=None))  # type: ignore
        elif (
            value.value_result != ""
            and value.value_str == ""
            and (value.value_num == 0.0 or value.value_num == 0)
        ):
            self.value = Result(value.value_result.lower())
            self.type = Type(primtype(primtype="result", parent=None))  # type: ignore
        else:
            raise ValueError("Invalid literal")
        return self


class Param:
    name: str
    type: Type
    method: "Method"

    def __init__(self, method: "Method", param: param):
        self.name = param.name
        self.type = Type(param.type)
        self.method = method


class Return:
    method: "Method"
    value: "Expression"

    def __init__(self, method: "Method", expr: expression):
        self.method = method
        self.value = Expression(method, expr)


class Method:
    name: str
    cls: "Class"
    params: list[Param]
    returnType: str
    body: list["Statement"]
    local_vars: list["LocalVar"]

    def __hash__(self) -> int:
        return hash((self.name, self.cls))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Method):
            return False
        return self.name == other.name and self.cls == other.cls

    def __init__(self, cls: "Class", mthd: method):
        self.cls = cls
        self.name = mthd.signature.name
        self.returnType = mthd.signature.returntype.primtype
        self.params = [Param(self, param) for param in mthd.signature.params]
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
            assmt: assignment | None = find_ancestor(stmt.statement, assignment)
            if assmt is not None:
                self.body += [Assignment(self, assmt)]
            ret: return_stmt | None = find_ancestor(stmt.statement, return_stmt)
            if ret is not None:
                self.body += [Return(self, ret.value)]


class LocalVar:
    name: str
    type: str
    method: Method

    def __hash__(self) -> int:
        # Hash by name, type and method
        return hash((self.name, self.type, self.method))

    def __eq__(self, other: object):
        if not isinstance(other, LocalVar):
            return False
        return self.name == other.name and self.method == other.method

    def __init__(self, method: Method, lvar: local_var):
        self.name = lvar.name
        self.type = lvar.type.primtype
        self.method = method


class Assignment:
    target: LocalVar
    method: Method
    value: "Expression"

    def __init__(self, method: Method, assmt: assignment):
        self.method = method
        for local_var in method.local_vars:
            if local_var.name == assmt.target:
                self.target = local_var
                break
        else:
            raise ValueError(
                f"No target found for assignment {assmt.target}={assmt.value}"
            )
        self.value = Expression.from_assignment(self, assmt.value)


class Expression:
    value: "Literal | LocalVar |MethodCall"

    @classmethod
    def from_mcall(cls, mcall: "MethodCall", expr: expression):
        return cls(mcall.src, expr)  # type: ignore

    @classmethod
    def from_assignment(cls, assmt: Assignment, expr: expression):
        return cls(assmt.method, expr)  # type: ignore

    def __init__(self, method: Method, expr: expression):
        ident: identifier | None = find_ancestor(expr.expression, identifier)
        if ident is not None:
            for local_var in method.local_vars:
                if local_var.name == ident.name:
                    self.value = local_var
                    break
            else:
                raise ValueError(f"No local variable found for identifier {ident}")
        else:
            lit: literal | None = find_ancestor(expr.expression, literal)
            if lit is not None:
                self.value = Literal.from_literal(lit)
            else:
                mcall: function_call | None = find_ancestor(
                    expr.expression, function_call
                )
                if mcall is not None:
                    self.value = MethodCall(method, mcall)
                else:
                    raise ValueError("Invalid expression")


class MethodCall:
    src: Method
    dst: Method
    params: list[Expression]

    def __init__(self, method: Method, mcall: function_call):
        self.src = method
        flag = False
        self.params = []
        if mcall.class_name == "":
            mcall.class_name = method.cls.name
        for cls in method.cls.program.classes + [method.cls]:
            if cls.name == mcall.class_name:
                for mthd in cls.methods:
                    if mthd.name == mcall.method_name:
                        self.dst = mthd
                        flag = True
                        break
                if flag:
                    break
        else:
            raise ValueError(f"No method found for call {mcall.method_name}")
        for param in mcall.params:
            self.params += [Expression.from_mcall(self, param)]


class Class:
    name: str

    methods: list[Method]
    program: "Program"

    def __hash__(self) -> int:
        return hash(self.name)

    def __init__(self, program: "Program", cls: clazz):
        self.methods = []
        self.name = cls.name
        self.program = program
        for content in cls.contents:
            mthd: method | None = find_ancestor(content.content, method)
            if mthd is not None:
                self.methods += [Method(self, mthd)]


Statement = MethodCall | LocalVar | Assignment | Return


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
