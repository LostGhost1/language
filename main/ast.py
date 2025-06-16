from dataclasses import dataclass
from typing import Any


@dataclass(kw_only=True)
class primtype:
    primtype: str
    parent: "field | param | method_signature | local_var"

    def __postinit__(self):
        if self.primtype not in ["string", "int", "float", "result"]:
            raise ValueError("Invalid primtype")


@dataclass(kw_only=True)
class field:
    name: str
    type: primtype
    parent: "class_content"


@dataclass(kw_only=True)
class param:
    name: str
    type: primtype
    parent: "method_signature"


@dataclass(kw_only=True)
class method_signature:
    name: str
    params: list[param]
    returntype: primtype
    parent: "method"


@dataclass(kw_only=True)
class interface_content:
    content: method_signature
    parent: "interface"


@dataclass(kw_only=True)
class interface:
    name: str
    contents: list[interface_content]
    parent: "block"


@dataclass(kw_only=True)
class literal:
    value_str: str
    value_num: int | float
    value_result: str
    parent: Any


@dataclass(kw_only=True)
class identifier:
    name: str
    parent: "expression"


@dataclass(kw_only=True)
class expression:
    expression: "literal | identifier | function_call"
    parent: "function_call"


@dataclass(kw_only=True)
class function_call:
    class_name: str
    method_name: str
    params: list[expression]
    parent: "statement"


@dataclass(kw_only=True)
class local_var:
    name: str
    type: primtype
    parent: "statement"


@dataclass(kw_only=True)
class pazz:
    parent: "statement"


@dataclass(kw_only=True)
class assignment:
    target: str
    value: expression
    parent: "statement"


@dataclass(kw_only=True)
class return_stmt:
    value: expression
    parent: "statement"


@dataclass(kw_only=True)
class statement:
    statement: function_call | local_var | assignment | return_stmt | pazz
    parent: "method_body"


@dataclass(kw_only=True)
class method_body:
    statements: list[statement]
    parent: "method"


@dataclass(kw_only=True)
class method:
    signature: method_signature
    body: method_body
    parent: "class_content"


@dataclass(kw_only=True)
class class_content:
    content: field | method
    parent: "clazz"


@dataclass(kw_only=True)
class clazz:
    name: str
    modifiers: list[Any]
    contents: list[class_content]
    parent: "block"


@dataclass(kw_only=True)
class block:
    block: clazz | interface
    parent: "program"


@dataclass(kw_only=True)
class program:
    blocks: list[block]


classlist = [
    primtype,
    field,
    method_signature,
    interface_content,
    interface,
    literal,
    function_call,
    local_var,
    statement,
    method_body,
    method,
    class_content,
    clazz,
    block,
    program,
    identifier,
    expression,
    return_stmt,
]
