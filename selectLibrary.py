"""Library selection and file discovery for B&R Automation Studio projects.

This module provides functionality to select a library directory and discover
declaration files (.fun, .typ, .var) within it.
"""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os

class SelectLibrary():
    """Helper class to select and validate B&R library directories.
    
    Discovers and provides paths to library declaration files (.fun, .typ, .var).
    """
    
    def __init__(self, library_path:str = "") -> None:
        """Initialize the library selector.
        
        Args:
            library_path: Path to the library directory. If empty, prompts user to select.
        """
        self.library_path = library_path
        if self.library_path == "":
            self.ask_directory()
        self.validate_library_path()
        self.library_declaration_path = self.get_library_declaration_path()


    def ask_directory(self) -> None:
        """Prompt user to select a library directory using a GUI dialog.
        
        Raises:
            Exception: If user cancels the directory selection.
        """
        root: tk.Tk = tk.Tk()
        root.wm_attributes('-topmost', 1)
        root.withdraw()

        selected_directory = filedialog.askdirectory(parent=root ,title="Please choose library directory",)
        if selected_directory:
            self.library_path = selected_directory
        else:
            raise Exception("User cancel directory selection")

    
    def validate_library_path(self) -> bool:
        """Validate that the library path exists.
        
        Returns:
            True if path exists.
            
        Raises:
            FileNotFoundError: If library path does not exist.
        """
        library_path = Path(self.library_path)
        if not library_path.exists():
            raise FileNotFoundError
        return True
        
    def get_library_path(self) -> str:
        """Get the library directory path.
        
        Returns:
            Library directory path as string.
        """
        return self.library_path

    def get_library_declaration_path(self) -> str:
        """Get the library declaration file (.fun) path.
        
        Returns:
            Filename of the .fun declaration file.
            
        Raises:
            Exception: If multiple or no .fun files are found.
        """
        fun_files = [each for each in os.listdir(self.library_path) if each.endswith('.fun')]
        if len(fun_files) > 1:
            raise Exception("Library can only have 1 .fun file for declaration")
        if len(fun_files) == 0:
            raise Exception("No .fun file found in library directory")
        return fun_files[0]
    
    def get_types_declaration_paths(self) -> str:
        """Search for all .typ files in the library directory and subdirectories.
        
        Returns:
            List of paths to .typ files as strings.
        """
        type_files = []
        for root, dirs, files in os.walk(self.library_path):
            for name in files:
                if name.endswith('.typ'):
                    type_files.append(os.path.join(root, name))
        return type_files

    def get_variable_declaration_paths(self) -> str:
        """Search for all .var files in the library directory and subdirectories.
        
        Returns:
            List of paths to .var files as strings.
        """
        var_files = []
        for root, dirs, files in os.walk(self.library_path):
            for name in files:
                if name.endswith('.var'):
                    var_files.append(os.path.join(root, name))
        return var_files
    
    def get_library_metadata_path(self) -> str:
        """Get the library metadata file (.lby) path.
        
        Returns:
            Filename of the .lby metadata file, or None if not found.
        """
        lby_files = [each for each in os.listdir(self.library_path) if each.endswith('.lby')]
        if len(lby_files) == 0:
            return None
        # Return first .lby file found (typically there's only one)
        return lby_files[0]