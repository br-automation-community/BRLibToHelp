"""Parsers for B&R Automation Studio library files.

This module provides parsers for:
- Function blocks (.fun files)
- Functions (.fun files)
- Structures and Enumerations (.typ files)
- Constants (.var files)
- Library metadata (.lby files)
"""
import re
from datatypes import *
import dataclasses
from typing import List, Union
from pathlib import Path
import json
import xml.etree.ElementTree as ET

class Parser:
    """Base parser class with common parsing methods for B&R types."""
    
    def parse_comment(self, text: str) -> Comment:
        """Parse a comment string into a Comment object.
        
        Args:
            text: The comment text to parse.
            
        Returns:
            Comment object with trimmed text.
        """
        return Comment(text=text.strip())

    def parse_array_dimension(self, dim_str: str) -> ArrayDimension:
        """Parse an array dimension string (e.g., '0..10' or 'MIN..MAX').
        
        Args:
            dim_str: String representing an array dimension.
            
        Returns:
            ArrayDimension object with bounds and constant flags.
        """
        lower_bound, upper_bound = dim_str.split('..')
        is_constant_lower = not lower_bound.isdigit()
        is_constant_upper = not upper_bound.isdigit()
        lower_bound = int(lower_bound) if lower_bound.isdigit() else lower_bound.strip()
        upper_bound = int(upper_bound) if upper_bound.isdigit() else upper_bound.strip()
        return ArrayDimension(lower_bound=lower_bound, upper_bound=upper_bound, is_constant_lower=is_constant_lower, is_constant_upper=is_constant_upper)

    def parse_type(self, type_str: str) -> Union[BasicType, ArrayType, StringType]:
        """Parse a type string into BasicType, ArrayType, or StringType.
        
        Args:
            type_str: Type string (e.g., 'INT', 'ARRAY[0..10] OF REAL', 'STRING[80]').
            
        Returns:
            Appropriate type object (BasicType, ArrayType, or StringType).
        """
        array_pattern = re.compile(r'ARRAY\s*\[(.*?)\]\s*OF\s*(\w+)')
        string_pattern = re.compile(r'STRING\s*\[(\w+)\]')
        
        if array_match := array_pattern.match(type_str):
            dimensions_str, base_type = array_match.groups()
            dimensions = [self.parse_array_dimension(dim) for dim in dimensions_str.split(',')]
            return ArrayType(base_type=base_type, dimensions=dimensions)
        
        if string_match := string_pattern.match(type_str):
            length_str = string_match.group(1).strip()
            is_constant_length = not length_str.isdigit()
            length = int(length_str) if length_str.isdigit() else length_str
            return StringType(length=length, is_constant=is_constant_length)
        
        return BasicType(type=type_str)

    def parse_variable_section(self, section: str, var_class, is_retain: bool = False) -> List[Variable]:
        """Parse a variable section and extract all variable declarations.
        
        Args:
            section: The section content to parse.
            var_class: The variable class to instantiate (VarInput, VarOutput, etc.).
            is_retain: Whether variables have RETAIN keyword.
            
        Returns:
            List of variable objects.
        """
        variables = []
        # Pattern that handles both regular variables and constants with default values
        # Matches: NAME : TYPE; or NAME : TYPE := VALUE;
        var_pattern = re.compile(r'\s*(\w+)\s*:\s*(\{.*?\}\s*)?(REFERENCE TO )?([\w\s\[\]\.,]+?)(?:\s*:=\s*([\w\.\#\-]+))?\s*;(?:\s*\(\*(.*?)\*\))?(?:\s*\(\*(.*?)\*\))?(?:\s*\(\*(.*?)\*\))?', re.DOTALL)
        for match in var_pattern.finditer(section):
            name, redundancy_info, ref, type_str, default_value, comment1, comment2, comment3 = match.groups()
            is_reference = ref is not None
            parsed_type = self.parse_type(type_str.strip())
            variables.append(var_class(
                name=name, 
                type=parsed_type, 
                is_reference=is_reference, 
                redundancy_info=redundancy_info, 
                default_value=default_value.strip() if default_value else None,
                comment1=comment1, 
                comment2=comment2, 
                comment3=comment3,
                retain=is_retain
            ))
        return variables
    

class FunctionBlockParser(Parser):
    """Parser for B&R function block declarations."""
    
    def parse(self, content: str) -> FunctionBlock:
        fb_pattern = re.compile(r'FUNCTION_BLOCK\s+(\w+)\s*(?:\(\*(.*?)\*\))?', re.DOTALL)
        var_section_pattern = re.compile(r'VAR(_INPUT|_OUTPUT|_CONSTANT|_IN_OUT)?\s*(RETAIN)?\s*(.*?)\s*END_VAR', re.DOTALL)

        fb_match = fb_pattern.search(content)
        if not fb_match:
            raise ValueError("No FUNCTION_BLOCK found in the content")

        if fb_match.lastindex == 1:
            name = fb_match.group(1)
            description = ""
        else:
            name, description = fb_match.groups()

        function_block = FunctionBlock(name=name, description=description.strip())

        for section_match in var_section_pattern.finditer(content):
            section_type, retain_keyword, section_content = section_match.groups()
            is_retain = retain_keyword is not None
            if section_type == "_INPUT":
                function_block.var_input.extend(self.parse_variable_section(section_content, VarInput, is_retain))
            elif section_type == "_OUTPUT":
                function_block.var_output.extend(self.parse_variable_section(section_content, VarOutput, is_retain))
            elif section_type == "_CONSTANT":
                function_block.var_constant.extend(self.parse_variable_section(section_content, VarConstant, is_retain))
            elif section_type == "_IN_OUT":
                function_block.var_in_out.extend(self.parse_variable_section(section_content, VarInOut))
            else:
                function_block.var.extend(self.parse_variable_section(section_content, Var, is_retain))

        return function_block

class FunctionParser(Parser):
    """Parser for B&R function declarations."""
    
    def parse(self, content: str) -> Function:
        func_pattern = re.compile(r'FUNCTION\s+(\w+)\s*:\s*(\w+)\s*(?:\(\*(.*?)\*\))?', re.DOTALL)
        var_section_pattern = re.compile(r'VAR(_INPUT|_IN_OUT)?\s*(.*?)\s*END_VAR', re.DOTALL)

        func_match = func_pattern.search(content)
        if not func_match:
            raise ValueError("No FUNCTION found in the content")

        if func_match.lastindex == 2:
            name, return_type = func_match.group(1, 2)
            description = ""
        else:
            name, return_type, description = func_match.groups()


        function = Function(name=name, return_type=return_type.strip(), description=description.strip())

        for section_match in var_section_pattern.finditer(content):
            section_type, section_content = section_match.groups()
            if section_type == "_INPUT":
                function.var_input.extend(self.parse_variable_section(section_content, VarInput))
            elif section_type == "_IN_OUT":
                function.var_in_out.extend(self.parse_variable_section(section_content, VarInOut))
            else:
                function.var.extend(self.parse_variable_section(section_content, Var))

        return function
    
class StructureParser(Parser):
    """Parser for B&R structure type declarations."""
    
    def parse(self, content: str) -> Structure:
        # Match: TypeName : STRUCT (*optional comment*) ... END_STRUCT;
        # Capture groups: (name, description, members_content)
        struct_pattern = re.compile(r'(\w+)\s*:\s*STRUCT\s*(?:\(\*(.*?)\*\))?\s*(.*?)\s*END_STRUCT\s*;', re.DOTALL)

        struct_match = struct_pattern.search(content)
        if not struct_match:
            raise ValueError("No STRUCT found in the content")

        name, description, members_content = struct_match.groups()

        structure = Structure(name=name, description=description.strip() if description else None)
        
        # Use parse_variable_section to parse the members
        structure.members = self.parse_variable_section(members_content, Var)

        return structure

class EnumerationParser(Parser):
    """Parser for B&R enumeration type declarations."""
    
    def parse(self, content: str) -> Enumeration:
        # First, remove multi-line comments that are on their own lines (not inline comments)
        # This handles commented-out enum values like: (*rbSTA_INIT_XXX := 16#1XXX, ...*)
        lines = content.split('\n')
        cleaned_lines = []
        in_multiline_comment = False
        
        for line in lines:
            # Check if line starts with comment (after whitespace)
            stripped = line.strip()
            if stripped.startswith('(*') and stripped.endswith('*)'):
                # Skip lines that are entirely comments
                continue
            elif stripped.startswith('(*'):
                in_multiline_comment = True
                continue
            elif stripped.endswith('*)') and in_multiline_comment:
                in_multiline_comment = False
                continue
            elif in_multiline_comment:
                continue
            else:
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Match: TypeName : ( ... ) := default_value;
        # The default value is optional
        # The description is the comment on the same line as the opening parenthesis
        enum_pattern = re.compile(
            r'(\w+)\s*:\s*\(\s*(?:\(\*(.*?)\*\))?\s*(.*?)\s*\)(?:\s*:=\s*(\w+))?\s*;', 
            re.DOTALL
        )
        
        enum_match = enum_pattern.search(cleaned_content)
        if not enum_match:
            raise ValueError(f"No ENUMERATION found in the content")
        
        name, description, literals_content, default_value = enum_match.groups()
        
        enumeration = Enumeration(
            name=name, 
            default_value=default_value, 
            description=description.strip() if description else None
        )
        
        # Parse literals - each can be: NAME or NAME := VALUE with optional comments (up to 3)
        # Pattern to match: NAME or NAME := VALUE with optional trailing comma and comments
        literal_pattern = re.compile(
            r'(\w+)'  # Literal name
            r'(?:\s*:=\s*([\w#]+))?'  # Optional := VALUE
            r'\s*(?:,)?'  # Optional comma
            r'(?:\s*\(\*(.*?)\*\))?'  # First comment (optional)
            r'(?:\s*\(\*(.*?)\*\))?'  # Second comment (optional)
            r'(?:\s*\(\*(.*?)\*\))?',  # Third comment (optional)
            re.DOTALL
        )
        
        for match in literal_pattern.finditer(literals_content):
            literal_name, literal_value, comment1, comment2, comment3 = match.groups()
            if literal_name and literal_name.strip():  # Skip empty matches
                # Clean up comments if present
                comment1 = comment1.strip() if comment1 else None
                comment2 = comment2.strip() if comment2 else None
                comment3 = comment3.strip() if comment3 else None
                enumeration.literals.append(EnumLiteral(
                    name=literal_name.strip(), 
                    value=literal_value.strip() if literal_value else None,
                    comment1=comment1,
                    comment2=comment2,
                    comment3=comment3
                ))
        
        return enumeration
class LibraryDeclarationFileParser:
    """Parser for B&R library declaration (.fun) files."""
        
    def __init__(self) -> None:
        """Initialize the library parser with function and function block parsers."""
        self.fb_parser = FunctionBlockParser()
        self.func_parser = FunctionParser()
        self.library = Library()

    def parse_fun_file(self, file_path: str) -> None:
        """Parse a .fun library declaration file.
        
        Args:
            file_path: Path to the .fun file.
        """
        with open(file_path, 'r') as file:
            content = file.read()
        self.library.name = Path(file_path).parent.name
        self.library.functions = list()
        self.library.function_blocks = list()

        blocks = self.parse_blocks(content)

        for block in blocks:
            if 'FUNCTION_BLOCK' in block:
                self.library.function_blocks.append(self.fb_parser.parse(block))
            elif 'FUNCTION' in block and not 'FUNCTION_BLOCK' in block:
                self.library.functions.append(self.func_parser.parse(block))

    def parse_blocks(self, file_content) -> list[str]:
        """Extract individual function and function block declarations from file content.
        
        Args:
            file_content: The content of the .fun file.
            
        Returns:
            List of function/function block declaration strings.
        """
        # Define the regex pattern to match the blocks with case sensitivity
        pattern = re.compile(r'(FUNCTION_BLOCK|FUNCTION).*?(END_FUNCTION_BLOCK|END_FUNCTION)', re.DOTALL)
        
        # Find all matches
        matches = pattern.findall(file_content)

        # Extract the full blocks
        blocks = pattern.finditer(file_content)
        full_blocks = [match.group(0) for match in blocks]
        
        return full_blocks


    def get_library(self) -> Library:
        """Get the parsed library object.
        
        Returns:
            Library object containing all parsed functions and function blocks.
        """
        return self.library
    
    def _get_library_as_json(self) -> str:
        """Convert the library object to JSON format.
        
        Returns:
            JSON string representation of the library.
        """
        class EnhancedJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if dataclasses.is_dataclass(o):
                    return dataclasses.asdict(o)
                return super().default(o)
            
        return json.dumps(self.get_library(), cls=EnhancedJSONEncoder)
    
    def _print_library_as_json(self) -> None:
        """Print the library as JSON to console."""
        print(self._get_library_as_json())
        
        
class TypeFileParser(Parser):
    """Parser for B&R type declaration (.typ) files containing structures and enumerations."""
    
    def __init__(self) -> None:
        """Initialize the type file parser."""
        self.struct_parser = StructureParser()
        self.enum_parser = EnumerationParser()
        self.structures: List[Structure] = []
        self.enumerations: List[Enumeration] = []
    
    def parse_typ_file(self, file_path: str) -> tuple[List[Structure], List[Enumeration]]:
        """Parse a .typ file containing type declarations.
        
        Args:
            file_path: Path to the .typ file.
            
        Returns:
            Tuple of (structures list, enumerations list).
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        self.structures = list()
        self.enumerations = list()
        
        # Parse TYPE blocks
        type_blocks = self.parse_type_blocks(content)
        
        for block in type_blocks:
            # Extract individual type definitions from the block
            definitions = self.extract_type_definitions_improved(block)
            
            for definition in definitions:
                # Try to parse as structure first
                if 'STRUCT' in definition.upper():
                    try:
                        struct = self.struct_parser.parse(definition)
                        self.structures.append(struct)
                        continue
                    except ValueError as e:
                        print(f"Failed to parse structure: {e}")
                        pass
                
                # Try to parse as enumeration
                # Check if it looks like an enumeration (has parentheses for values)
                if ':' in definition and '(' in definition:
                    try:
                        enum = self.enum_parser.parse(definition)
                        self.enumerations.append(enum)
                        continue
                    except ValueError as e:
                        print(f"Failed to parse enumeration: {e}")
                        pass
        
        return self.structures, self.enumerations
    
    def parse_type_blocks(self, file_content: str) -> list[str]:
        """Extract all TYPE blocks from the file content.
        
        Args:
            file_content: Content of the .typ file.
            
        Returns:
            List of TYPE block contents.
        """
        # Match TYPE ... END_TYPE blocks
        pattern = re.compile(r'TYPE\s+(.*?)\s+END_TYPE', re.DOTALL | re.IGNORECASE)
        
        blocks = pattern.finditer(file_content)
        type_blocks = [match.group(1) for match in blocks]
        
        return type_blocks
    
    def extract_type_definitions_improved(self, type_block: str) -> list[str]:
        """Extract individual type definitions from a TYPE block.
        
        This improved version sequentially parses structures and enumerations
        to handle complex nested cases.
        """
        definitions = []
        remaining = type_block.strip()
        
        while remaining:
            remaining = remaining.strip()
            if not remaining:
                break
            
            # Try to find a structure definition
            struct_match = re.match(
                r'(\w+\s*:\s*STRUCT\s+.*?\s+END_STRUCT\s*;)',
                remaining,
                re.DOTALL | re.IGNORECASE
            )
            
            if struct_match:
                definitions.append(struct_match.group(1))
                remaining = remaining[struct_match.end():]
                continue
            
            # Try to find an enumeration definition
            # Look for: NAME : ( ... ) or NAME : ( ... ) := DEFAULT;
            enum_match = re.match(r'(\w+)\s*:\s*\(', remaining)
            if enum_match:
                name = enum_match.group(1)
                start_pos = enum_match.end() - 1  # Position of '('
                
                # Find the matching closing parenthesis
                paren_count = 0
                pos = start_pos
                in_comment = False
                
                while pos < len(remaining):
                    # Handle comments
                    if pos < len(remaining) - 1 and remaining[pos:pos+2] == '(*':
                        in_comment = True
                        pos += 2
                        continue
                    
                    if pos < len(remaining) - 1 and remaining[pos:pos+2] == '*)':
                        in_comment = False
                        pos += 2
                        continue
                    
                    if not in_comment:
                        if remaining[pos] == '(':
                            paren_count += 1
                        elif remaining[pos] == ')':
                            paren_count -= 1
                            if paren_count == 0:
                                # Found matching closing paren
                                # Look for optional := DEFAULT and semicolon
                                rest = remaining[pos+1:].lstrip()
                                default_match = re.match(r':=\s*(\w+)\s*;', rest)
                                if default_match:
                                    end_pos = pos + 1 + len(remaining[pos+1:]) - len(rest) + default_match.end()
                                else:
                                    # Just look for semicolon
                                    semi_match = re.match(r'\s*;', rest)
                                    if semi_match:
                                        end_pos = pos + 1 + len(remaining[pos+1:]) - len(rest) + semi_match.end()
                                    else:
                                        end_pos = pos + 1
                                
                                definitions.append(remaining[:end_pos])
                                remaining = remaining[end_pos:]
                                break
                    
                    pos += 1
                
                if paren_count != 0:
                    # Malformed enumeration, skip to next type
                    print(f"Warning: Malformed enumeration starting with {name}")
                    # Try to find the next type definition
                    next_type = re.search(r'\w+\s*:', remaining[pos:])
                    if next_type:
                        remaining = remaining[pos + next_type.start():]
                    else:
                        break
                
                continue
            
            # If we can't match anything, try to skip to the next type definition
            next_type = re.search(r'\w+\s*:', remaining[1:])
            if next_type:
                remaining = remaining[1 + next_type.start():]
            else:
                # Nothing more to parse
                break
        
        return definitions
    
    
    def get_structures(self) -> List[Structure]:
        """Get the list of parsed structures.
        
        Returns:
            List of Structure objects.
        """
        return self.structures
    
    def get_enumerations(self) -> List[Enumeration]:
        """Get the list of parsed enumerations.
        
        Returns:
            List of Enumeration objects.
        """
        return self.enumerations
    
class VarFileParser(Parser):
    """Parser for B&R variable declaration (.var) files containing constants."""
    
    def __init__(self) -> None:
        """Initialize the variable file parser."""
        self.constants: List[VarConstant] = []
    
    def parse_var_file(self, file_path: str) -> List[VarConstant]:
        """Parse a .var file and extract all constants.
        
        Args:
            file_path: Path to the .var file
            
        Returns:
            List of VarConstant objects
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        self.constants = list()
        
        # Parse VAR CONSTANT blocks
        var_constant_blocks = self.parse_var_constant_blocks(content)
        
        for block in var_constant_blocks:
            self.constants.extend(self.parse_variable_section(block, VarConstant))
        
        return self.constants
    
    def parse_var_constant_blocks(self, file_content: str) -> list[str]:
        """Extract all VAR CONSTANT ... END_VAR blocks from the file.
        
        Args:
            file_content: The content of the .var file
            
        Returns:
            List of constant block contents (without VAR CONSTANT and END_VAR keywords)
        """
        # Match VAR CONSTANT ... END_VAR blocks
        pattern = re.compile(r'VAR\s+CONSTANT\s+(.*?)\s+END_VAR', re.DOTALL | re.IGNORECASE)
        
        blocks = pattern.finditer(file_content)
        constant_blocks = [match.group(1) for match in blocks]
        
        return constant_blocks
    
    def get_constants(self) -> List[VarConstant]:
        """Get the list of parsed constants.
        
        Returns:
            List of VarConstant objects
        """
        return self.constants

class LibraryFileParser:
    """Parser for B&R library metadata (.lby) files."""
    
    def __init__(self) -> None:
        """Initialize the library file parser."""
        self.metadata = {}
    
    def parse_lby_file(self, file_path: str) -> dict:
        """Parse a .lby file and extract library metadata.
        
        Args:
            file_path: Path to the .lby file.
            
        Returns:
            Dictionary containing library metadata with the following keys:
            - name: Library name (extracted from parent folder name)
            - version: Library version (default: "1.0.0" if not present)
            - type: SubType attribute (IEC, binary, ANSIC, etc.) - optional
            - description: Library description - optional
            - header_file_name: HeaderFileName attribute - optional
            - file_version: AutomationStudio FileVersion - optional
            - files: List of file paths with descriptions
            - dependencies: List of dependency dictionaries with ObjectName, FromVersion, ToVersion
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract library name from parent folder
            library_name = Path(file_path).parent.name
            
            # Extract attributes from Library element
            # Version defaults to "1.0.0" if not present
            version = root.get('Version', '1.0.0')
            subtype = root.get('SubType')  # Optional: IEC, binary, ANSIC, etc.
            description = root.get('Description')  # Optional
            header_file_name = root.get('HeaderFileName')  # Optional
            
            # Extract AutomationStudio FileVersion from processing instruction
            file_version = None
            for child in tree.iter():
                if child.tag == '{http://www.w3.org/XML/1998/namespace}AutomationStudio':
                    file_version = child.get('FileVersion')
                    break
            
            # If not found in tags, check processing instructions
            if file_version is None:
                for pi in tree.iter():
                    if hasattr(pi, 'target') and pi.target == 'AutomationStudio':
                        # Parse the PI text for FileVersion
                        if hasattr(pi, 'text'):
                            match = re.search(r'FileVersion="([^"]+)"', pi.text)
                            if match:
                                file_version = match.group(1)
            
            self.metadata = {
                "name": library_name,
                "version": version,
                "type": subtype,
                "description": description,
                "header_file_name": header_file_name,
                "file_version": file_version,
                "files": [],
                "dependencies": []
            }
            
            # Extract Files
            files_element = root.find('{http://br-automation.co.at/AS/Library}Files')
            if files_element is not None:
                for file_elem in files_element.findall('{http://br-automation.co.at/AS/Library}File'):
                    file_info = {
                        "path": file_elem.text,
                        "description": file_elem.get('Description')
                    }
                    self.metadata["files"].append(file_info)
            
            # Extract Dependencies
            deps_element = root.find('{http://br-automation.co.at/AS/Library}Dependencies')
            if deps_element is not None:
                for dep_elem in deps_element.findall('{http://br-automation.co.at/AS/Library}Dependency'):
                    dependency = {
                        "object_name": dep_elem.get('ObjectName'),
                        "from_version": dep_elem.get('FromVersion'),
                        "to_version": dep_elem.get('ToVersion')
                    }
                    self.metadata["dependencies"].append(dependency)
            
            return self.metadata
            
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML file: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing .lby file: {e}")
    
    def get_metadata(self) -> dict:
        """Get the parsed library metadata.
        
        Returns:
            Dictionary containing library metadata.
        """
        return self.metadata
    
    def update_library_object(self, library: Library) -> None:
        """Update a Library object with the parsed metadata.
        
        Args:
            library: Library object to update with metadata.
        """
        if self.metadata:
            library.name = self.metadata.get("name", library.name)
            library.version = self.metadata.get("version", "1.0.0")
            library.type = self.metadata.get("type")
            library.description = self.metadata.get("description")
            library.header_file_name = self.metadata.get("header_file_name")
            library.file_version = self.metadata.get("file_version")
            
            # Store file paths (extract just the path string)
            library.files = [f["path"] for f in self.metadata.get("files", [])]
            
            # Store dependencies
            library.dependency_libraries = self.metadata.get("dependencies", [])