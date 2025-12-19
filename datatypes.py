"""Data type definitions for B&R Automation Studio library elements.

This module defines dataclass structures for representing:
- Basic types, arrays, and strings
- Variables (input, output, in_out, local, constants)
- Functions and function blocks
- Structures and enumerations
- Library metadata
"""
from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass
class Comment:
    """Represents a variable comment."""
    text: str

@dataclass
class BasicType:
    """Represents a basic data type (e.g., INT, REAL, BOOL)."""
    type: str

    def __str__(self) -> str:
        return self.type

@dataclass
class ArrayDimension:
    """Represents a single dimension of an array with bounds.
    
    Attributes:
        lower_bound: Lower bound (can be int or constant name)
        upper_bound: Upper bound (can be int or constant name)
        is_constant_lower: True if lower bound is a named constant
        is_constant_upper: True if upper bound is a named constant
    """
    lower_bound: Union[int, str]
    upper_bound: Union[int, str]
    is_constant_lower: bool
    is_constant_upper: bool

@dataclass
class ArrayType:
    """Represents an array type with one or more dimensions.
    
    Attributes:
        base_type: The element type of the array
        dimensions: List of array dimensions
    """
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
    """Represents a STRING type with specified length.
    
    Attributes:
        length: String length (can be int or constant name)
        is_constant: True if length is a named constant
    """
    length: Union[int, str]
    is_constant: bool

    def __str__(self) -> str:
        return f"STRING[{self.length}]"
    

@dataclass
class Variable:
    """Base class for all variable types.
    
    Attributes:
        name: Variable name
        type: Variable type (BasicType, ArrayType, or StringType)
        is_reference: True if variable is a REFERENCE TO
        redundancy_info: Redundancy annotation if present
        comment1: First comment line
        comment2: Second comment line
        comment3: Third comment line
        default_value: Default initialization value
        retain: True if variable has RETAIN keyword
    """
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
    """Input variable (VAR_INPUT)."""
    I_O: str = "IN"

@dataclass
class VarOutput(Variable):
    """Output variable (VAR_OUTPUT)."""
    I_O: str = "OUT"

@dataclass
class VarInOut(Variable):
    """Input/Output variable (VAR_IN_OUT)."""
    I_O: str = "IN_OUT"

@dataclass
class Var(Variable):
    """Local variable (VAR)."""
    pass

@dataclass
class VarConstant(Variable):
    """Constant variable (VAR CONSTANT)."""
    pass

@dataclass
class FunctionBlock:
    """Represents a B&R function block with all its variables.
    
    Attributes:
        name: Function block name
        description: Optional description from comments
        var_input: List of input variables
        var_output: List of output variables
        var: List of local variables
        var_in_out: List of in/out variables
        var_constant: List of constants
    """
    name: str
    description: Optional[str] = None
    var_input: List[VarInput] = field(default_factory=list)
    var_output: List[VarOutput] = field(default_factory=list)
    var: List[Var] = field(default_factory=list)
    var_in_out: List[VarInOut] = field(default_factory=list)
    var_constant: List[VarConstant] = field(default_factory=list)

@dataclass
class Function:
    """Represents a B&R function with return type.
    
    Attributes:
        name: Function name
        return_type: The return data type
        description: Optional description from comments
        var_input: List of input variables
        var_in_out: List of in/out variables
        var: List of local variables
    """
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
    """Represents a single literal value in an enumeration.
    
    Attributes:
        name: Literal name
        value: Optional explicit value
        comment1: First comment line
        comment2: Second comment line
        comment3: Third comment line
    """
    name: str
    value: Optional[str] = None
    comment1 : Optional[str] = None
    comment2 : Optional[str] = None
    comment3 : Optional[str] = None
    
@dataclass
class Enumeration:
    """Represents a B&R enumeration type.
    
    Attributes:
        name: Enumeration name
        literals: List of enum literals
        description: Optional description from comments
        default_value: Optional default literal
    """
    name: str
    literals: List[EnumLiteral] = field(default_factory=list)
    description: Optional[str] = None
    default_value: Optional[str] = None
    
@dataclass
class Library:
    """Represents a complete B&R Automation Studio library.
    
    Attributes:
        name: Library name
        description: Optional library description
        version: Library version
        type: Library type
        dependency_libraries: List of dependent library names
        functions: List of library functions
        function_blocks: List of library function blocks
        structures: List of library structures
        enumerations: List of library enumerations
        constants: List of library constants
    """
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