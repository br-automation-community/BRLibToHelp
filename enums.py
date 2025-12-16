from enum import Enum

class DataTypeType(Enum):
    ENUM: 0
    STRUCT: 1
    FUNCTION_BLOCK: 2
    DERIVED: 3

class ParameterType(Enum):
    IN: 0
    OUT: 1
    IN_OUT: 2
    VAR: 3
