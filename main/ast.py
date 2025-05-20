from dataclasses import dataclass
from typing import Any


@dataclass(kw_only=True)
class primtype:
    primtype: str
    parent: Any


@dataclass(kw_only=True)
class field:
    name: str
    type: primtype
    parent: Any


@dataclass(kw_only=True)
class method_signature:
    name: str
    params: list[field]
    returntype: primtype
    parent: Any


@dataclass(kw_only=True)
class interface_content:
    content: method_signature


@dataclass(kw_only=True)
class interface:
    name: str
    contents: list[interface_content]
    parent: Any


@dataclass(kw_only=True)
class literal:
    value: str
    parent: Any


@dataclass(kw_only=True)
class field_ref:
    field: field
    parent: Any


@dataclass(kw_only=True)
class expression:
    value: literal | field_ref
    parent: Any


@dataclass(kw_only=True)
class return_stmt:
    value: expression
    parent: Any


@dataclass(kw_only=True)
class function_call:
    class_name: str
    method_name: str
    params: list[expression]
    parent: Any


@dataclass(kw_only=True)
class assignment:
    name: str
    value: str
    parent: Any


@dataclass(kw_only=True)
class statement:
    statement: return_stmt | function_call | assignment | field
    parent: Any


@dataclass(kw_only=True)
class method_body:
    statements: list[statement]
    parent: Any


@dataclass(kw_only=True)
class method:
    signature: method_signature
    body: method_body
    parent: Any


@dataclass(kw_only=True)
class class_content:
    content: field | method
    parent: Any


@dataclass(kw_only=True)
class clazz:
    name: str
    modifiers: list[Any]
    contents: list[class_content]
    parent: Any


@dataclass(kw_only=True)
class block:
    block: clazz | interface
    parent: Any


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
    field_ref,
    expression,
    return_stmt,
    function_call,
    assignment,
    statement,
    method_body,
    method,
    class_content,
    clazz,
    block,
    program,
]
