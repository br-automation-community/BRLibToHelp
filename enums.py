"""Enumeration definitions for B&R library element types.

This module defines enumerations used throughout the application
to categorize different types of data and parameters.
"""
from enum import Enum


class DataTypeType(Enum):
    """Types of data type declarations in B&R libraries.
    
    Attributes:
        ENUM: Enumeration type
        STRUCT: Structure type
        FUNCTION_BLOCK: Function block type
        DERIVED: Derived/alias type
    """
    ENUM: 0
    STRUCT: 1
    FUNCTION_BLOCK: 2
    DERIVED: 3


class ParameterType(Enum):
    """Types of function/function block parameters.
    
    Attributes:
        IN: Input parameter
        OUT: Output parameter
        IN_OUT: Input/output parameter
        VAR: Local variable
    """
    IN: 0
    OUT: 1
    IN_OUT: 2
    VAR: 3
