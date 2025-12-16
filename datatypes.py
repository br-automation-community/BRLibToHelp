from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass
class Comment:
    text: str

@dataclass
class BasicType:
    type: str

    def __str__(self) -> str:
        return self.type

@dataclass
class ArrayDimension:
    lower_bound: Union[int, str]
    upper_bound: Union[int, str]
    is_constant_lower: bool
    is_constant_upper: bool

@dataclass
class ArrayType:
    base_type: str
    dimensions: List[ArrayDimension]

    def __str__(self) -> str:
        returnStr = f"{self.base_type}["
        for dim in self.dimensions:
            returnStr += f"{dim.lower_bound}..{dim.upper_bound},"
        # delete last comma
        returnStr = f"{returnStr[:-1]}]"
        return returnStr

@dataclass
class StringType:
    length: Union[int, str]
    is_constant: bool

    def __str__(self) -> str:
        return f"STRING[{self.length}]"
    

@dataclass
class Variable:
    name: str
    type: Union[BasicType, ArrayType, StringType]
    is_reference: bool = False
    redundancy_info: Optional[str] = None
    comment1: Optional[str] = None
    comment2: Optional[str] = None
    comment3: Optional[str] = None
    default_value: Optional[str] = None
    retain: bool = False

@dataclass
class VarInput(Variable):
    I_O: str = "IN"

@dataclass
class VarOutput(Variable):
    I_O: str = "OUT"

@dataclass
class VarInOut(Variable):
    I_O: str = "IN_OUT"

@dataclass
class Var(Variable):
    pass

@dataclass
class VarConstant(Variable):
    pass

@dataclass
class FunctionBlock:
    name: str
    description: Optional[str] = None
    var_input: List[VarInput] = field(default_factory=list)
    var_output: List[VarOutput] = field(default_factory=list)
    var: List[Var] = field(default_factory=list)
    var_in_out: List[VarInOut] = field(default_factory=list)
    var_constant: List[VarConstant] = field(default_factory=list)

@dataclass
class Function:
    name: str
    return_type: str
    description: Optional[str] = None
    var_input: List[VarInput] = field(default_factory=list)
    var_in_out: List[VarInOut] = field(default_factory=list)
    var: List[Var] = field(default_factory=list)
    
@dataclass
class Structure:
    name: str
    members: List[Variable] = field(default_factory=list)
    description: Optional[str] = None

@dataclass
class EnumLiteral:
    name: str
    value: Optional[str] = None
    comment1 : Optional[str] = None
    comment2 : Optional[str] = None
    comment3 : Optional[str] = None
    
@dataclass
class Enumeration:
    name: str
    literals: List[EnumLiteral] = field(default_factory=list)
    description: Optional[str] = None
    default_value: Optional[str] = None
    
@dataclass
class Library:
    name: str = field(default="")
    description: Optional[str] = field(default=None)
    version: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)
    dependency_libraries: Optional[List[str]] = field(default_factory=list)
    functions: Optional[List[Function]] = field(default_factory=list)
    function_blocks: Optional[List[FunctionBlock]] = field(default_factory=list)
    structures: Optional[List[Structure]] = field(default_factory=list)
    enumerations: Optional[List[Enumeration]] = field(default_factory=list)
    constants: Optional[List[VarConstant]] = field(default_factory=list)