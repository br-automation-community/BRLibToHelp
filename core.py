"""Core business logic for processing B&R libraries to CHM help files.

This module provides a standalone processor that can be used by both
GUI and CLI interfaces to generate CHM documentation from B&R libraries.
"""
from pathlib import Path
from typing import Dict, List, Optional
from parser import LibraryDeclarationFileParser, TypeFileParser, VarFileParser, LibraryFileParser
from selectLibrary import SelectLibrary, is_valid_library
from libraryToChm import LibraryDeclarationToChm
from datatypes import Library, Structure, Enumeration, VarConstant


class LibraryProcessor:
    """Standalone processor for generating CHM help files from B&R libraries.
    
    This class encapsulates all the business logic for parsing library files
    and generating CHM documentation, without any GUI dependencies.
    
    Args:
        library_path: Path to the B&R library folder
        output_path: Path to the build output folder
        keep_sources: Whether to keep HTML source files after CHM generation
    """
    
    def __init__(self, library_path: str, output_path: str, keep_sources: bool = True, use_help_folder: bool = False):
        """Initialize the library processor.
        
        Args:
            library_path: Path to the library folder containing .fun, .typ, .var files
            output_path: Path where the CHM file will be generated
            keep_sources: If True, keep HTML sources; if False, delete them after CHM generation
            use_help_folder: If True, places CHM directly in Help folder (no subdirectories)
        """
        self.library_path = Path(library_path).resolve()
        self.output_path = Path(output_path).resolve()
        self.keep_sources = keep_sources
        self.use_help_folder = use_help_folder
        
    def validate_inputs(self) -> tuple[bool, Optional[str]]:
        """Validate library and output paths.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check library path exists
        if not self.library_path.exists():
            return False, f"Library folder not found: {self.library_path}"
        
        # Check output path exists
        if not self.output_path.exists():
            return False, f"Output folder not found: {self.output_path}"
        
        # Validate library structure
        is_valid, error_msg = is_valid_library(str(self.library_path))
        if not is_valid:
            return False, error_msg
        
        return True, None
    
    def process(self) -> Dict:
        """Process the library and generate CHM documentation.
        
        Returns:
            dict: Result dictionary containing:
                - success (bool): Whether processing succeeded
                - chm_path (str): Path to generated CHM file (if successful)
                - library (Library): Parsed library object (if successful)
                - stats (dict): Statistics about parsed elements
                - error (str): Error message (if failed)
        """
        result = {
            'success': False,
            'chm_path': None,
            'library': None,
            'stats': {},
            'error': None
        }
        
        try:
            # Validate inputs
            is_valid, error_msg = self.validate_inputs()
            if not is_valid:
                result['error'] = error_msg
                return result
            
            # Select and validate library
            try:
                select_lib = SelectLibrary(str(self.library_path))
            except FileNotFoundError as e:
                result['error'] = "Library folder not found or no longer accessible"
                return result
            except Exception as e:
                result['error'] = f"Error accessing library folder: {str(e)}"
                return result
            
            # Get library file paths
            try:
                lib_declaration_path = self.library_path / select_lib.get_library_declaration_path()
                type_file_paths = select_lib.get_types_declaration_paths()
                var_file_paths = select_lib.get_variable_declaration_paths()
                lby_file_path = select_lib.get_library_metadata_path()
            except Exception as e:
                result['error'] = f"Could not read library declaration files: {str(e)}"
                return result
            
            # Initialize collections
            structures: List[Structure] = []
            enumerations: List[Enumeration] = []
            constants: List[VarConstant] = []
            
            # Parse library declaration file (.fun)
            try:
                libFileParser = LibraryDeclarationFileParser()
                libFileParser.parse_fun_file(file_path=lib_declaration_path.as_posix())
                library = libFileParser.get_library()
            except FileNotFoundError:
                result['error'] = f"Library declaration file not found: {lib_declaration_path}"
                return result
            except Exception as e:
                result['error'] = f"Error parsing library declaration file (.fun): {str(e)}"
                return result
            
            # Parse library metadata file (.lby) if it exists
            if lby_file_path:
                lby_full_path = self.library_path / lby_file_path
                try:
                    lbyParser = LibraryFileParser()
                    lbyParser.parse_lby_file(file_path=lby_full_path.as_posix())
                    lbyParser.update_library_object(library)
                except Exception as e:
                    # Continue with default values if .lby parsing fails
                    # This is a non-critical error
                    print(f"[WARNING] Could not parse library metadata file (.lby): {str(e)}")
                    print(f"   Continuing with default metadata...")
                    pass
            
            # Parse all types files in library folder
            try:
                for file_path in type_file_paths:
                    typeFileParser = TypeFileParser()
                    typeFileParser.parse_typ_file(file_path=file_path)
                    structures.extend(typeFileParser.get_structures())
                    enumerations.extend(typeFileParser.get_enumerations())
            except Exception as e:
                # Continue without structures/enumerations if parsing fails
                # This is a non-critical error
                print(f"[WARNING] Could not parse type files (.typ): {str(e)}")
                print(f"   Continuing without structures and enumerations...")
                pass
            
            library.structures = structures
            library.enumerations = enumerations
            
            # Parse all variable files in library folder
            try:
                for file_path in var_file_paths:
                    varFileParser = VarFileParser()
                    varFileParser.parse_var_file(file_path=file_path)
                    constants.extend(varFileParser.get_constants())
            except Exception as e:
                # Continue without constants if parsing fails
                # This is a non-critical error
                print(f"[WARNING] Could not parse variable files (.var): {str(e)}")
                print(f"   Continuing without constants...")
                pass
            
            library.constants = constants
            
            # Generate CHM file
            try:
                libraryToChm = LibraryDeclarationToChm(
                    library=library,
                    keep_sources=self.keep_sources,
                    use_help_folder=self.use_help_folder
                )
                chm_path = libraryToChm.generate_library_chm(build_folder=str(self.output_path))
            except PermissionError:
                result['error'] = f"Permission denied when writing to build folder: {self.output_path}"
                return result
            except Exception as e:
                result['error'] = f"Error generating CHM help file: {str(e)}"
                return result
            
            # Build success result
            result['success'] = True
            result['chm_path'] = chm_path
            result['library'] = library
            result['stats'] = {
                'functions': len(library.functions),
                'function_blocks': len(library.function_blocks),
                'structures': len(library.structures),
                'enumerations': len(library.enumerations),
                'constants': len(library.constants)
            }
            
            return result
            
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
            return result
