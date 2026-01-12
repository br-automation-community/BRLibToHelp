"""GUI application for converting B&R Automation libraries to CHM help files.

This module provides a Tkinter-based graphical user interface that allows users to:
- Select a B&R library folder
- Choose a build output directory
- Generate CHM documentation from the library
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List
from parser import LibraryDeclarationFileParser, TypeFileParser, VarFileParser, LibraryFileParser
from selectLibrary import SelectLibrary, is_valid_library
from libraryToChm import LibraryDeclarationToChm
from datatypes import Structure, Enumeration, VarConstant
import subprocess
from os.path import normpath
from utils import get_resource_path

class BRLibToMarkdownApp:
    """Main application class for the B&R Library to CHM converter.
    
    Args:
        root: The root Tkinter window instance.
    """
    
    def __init__(self, root):
        """Initialize the application GUI.
        
        Args:
            root: Tkinter root window.
        """
        self.root = root
        self.root.title("B&R Lib to CHM Help")
        
        # Set window icon if available
        try:
            icon_path = get_resource_path("icon.ico")
            if icon_path.exists():
                self.root.iconbitmap(icon_path)
        except Exception as e:
            # If icon cannot be loaded, continue without it
            pass

        # Configure grid weights to make the window resizable
        # Column 1 (entry fields) will expand when window is resized
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(2, weight=0)

        # Library folder path
        self.folder_path_library_label = tk.Label(root, text="Library folder path:")
        self.folder_path_library_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.folder_path_library_entry = tk.Entry(root, width=50)
        self.folder_path_library_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.folder_path_library_entry.config(state="readonly")

        self.folder_path_library_button = tk.Button(root, text="Browse", command=self.browse_folder_library)
        self.folder_path_library_button.grid(row=0, column=2, padx=10, pady=10)

        # Build folder path
        self.folder_path_build_label = tk.Label(root, text="Build folder path:")
        self.folder_path_build_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.folder_path_build_entry = tk.Entry(root, width=50)
        self.folder_path_build_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.folder_path_build_entry.config(state="readonly")

        self.folder_path_build_button = tk.Button(root, text="Browse", command=self.browse_folder_build)
        self.folder_path_build_button.grid(row=1, column=2, padx=10, pady=10)

        # Start button
        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.grid(row=2, column=0, columnspan=3, pady=10)
        self.start_button.config(state="disabled")

        # Quit button
        self.quit_button = tk.Button(root, text="Quit", command=root.quit)
        self.quit_button.grid(row=3, column=0, columnspan=3, pady=10)

    def browse_folder_library(self):
        """Open a directory browser dialog to select the library folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_library_entry.config(state="normal")
            self.folder_path_library_entry.delete(0, tk.END)
            self.folder_path_library_entry.insert(0, folder_selected)
            self.folder_path_library_entry.config(state="readonly")
        self.start_is_valid()

    def browse_folder_build(self):
        """Open a directory browser dialog to select the build output folder."""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_build_entry.config(state="normal")
            self.folder_path_build_entry.delete(0, tk.END)
            self.folder_path_build_entry.insert(0, folder_selected)
            self.folder_path_build_entry.config(state="readonly")
        self.start_is_valid()


    def start_is_valid(self) -> None:
        """Enable or disable the Start button based on folder path validation."""
        if self.folder_path_are_valid():
            self.start_button.config(state="normal")
        else:
            self.start_button.config(state="disabled")

    def folder_path_are_valid(self) -> bool:
        """Validate that both library and build folder paths exist and library is valid.
        
        Returns:
            bool: True if both paths are valid and library folder is a valid B&R library, False otherwise.
        """
        folder_path_library = self.folder_path_library_entry.get()
        folder_path_build = self.folder_path_build_entry.get()
        
        if folder_path_build == "" or folder_path_library == "":
            return False
        
        # Check build path exists
        build_path = Path(folder_path_build)
        if not build_path.exists():
            return False
        
        # Check library path exists
        library_path = Path(folder_path_library)
        if not library_path.exists():
            return False
        
        # Check if library is valid
        is_valid, error_msg = is_valid_library(folder_path_library)
        if not is_valid:
            # Clear the library path entry and show error
            self.folder_path_library_entry.config(state="normal")
            self.folder_path_library_entry.delete(0, tk.END)
            self.folder_path_library_entry.config(state="readonly")
            
            messagebox.showerror(
                title="Invalid Library Folder",
                message=error_msg
            )
            return False
        
        return True

    def start(self):
        """Start the library to CHM conversion process.
        
        This method:
        - Parses the library metadata from .lby file
        - Parses the library declaration files
        - Extracts functions, function blocks, structures, enumerations, and constants
        - Generates the CHM help file
        - Displays a summary and optionally opens the build folder
        """
        folder_path_library = self.folder_path_library_entry.get()
        folder_path_build = self.folder_path_build_entry.get()
        
        try:
            select_lib = SelectLibrary(folder_path_library)
        except FileNotFoundError:
            messagebox.showerror(
                title="Error",
                message="Library folder not found or no longer accessible."
            )
            return
        except Exception as e:
            messagebox.showerror(
                title="Error",
                message=f"Error accessing library folder:\n{str(e)}"
            )
            return
        
        try:
            lib_declaration_path = Path(folder_path_library).resolve() / select_lib.get_library_declaration_path()
            type_file_paths = select_lib.get_types_declaration_paths()
            var_file_paths = select_lib.get_variable_declaration_paths()
            lby_file_path = select_lib.get_library_metadata_path()
        except Exception as e:
            messagebox.showerror(
                title="Error Reading Library Files",
                message=f"Could not read library declaration files:\n{str(e)}"
            )
            return
        
        structures: List[Structure] = []
        enumerations: List[Enumeration] = []
        constants: List[VarConstant] = []

        # Parse library declaration file (.fun)
        try:
            libFileParser = LibraryDeclarationFileParser()
            libFileParser.parse_fun_file(file_path=lib_declaration_path.as_posix())
            library = libFileParser.get_library()
        except FileNotFoundError:
            messagebox.showerror(
                title="Parsing Error",
                message=f"Library declaration file not found:\n{lib_declaration_path}"
            )
            return
        except Exception as e:
            messagebox.showerror(
                title="Parsing Error",
                message=f"Error parsing library declaration file (.fun):\n{str(e)}"
            )
            return
        
        # Parse library metadata file (.lby) if it exists
        if lby_file_path:
            lby_full_path = Path(folder_path_library).resolve() / lby_file_path
            try:
                lbyParser = LibraryFileParser()
                lbyParser.parse_lby_file(file_path=lby_full_path.as_posix())
                lbyParser.update_library_object(library)
            except Exception as e:
                # If .lby parsing fails, continue with default values
                messagebox.showwarning(
                    title="Warning",
                    message=f"Could not parse library metadata file (.lby):\n{str(e)}\n\nContinuing with default metadata."
                )
        
        # Parse all types files in library folder
        try:
            for file_path in type_file_paths:
                typeFileParser = TypeFileParser()
                typeFileParser.parse_typ_file(file_path=file_path)
                structures.extend(typeFileParser.get_structures())
                enumerations.extend(typeFileParser.get_enumerations())
        except Exception as e:
            messagebox.showerror(
                title="Parsing Error",
                message=f"Error parsing type files (.typ):\n{str(e)}\n\nContinuing without structures and enumerations."
            )
            # Continue without structures/enumerations if parsing fails
            
        library.structures = structures
        library.enumerations = enumerations
        
        # Parse all variable files in library folder
        try:
            for file_path in var_file_paths:
                varFileParser = VarFileParser()
                varFileParser.parse_var_file(file_path=file_path)
                constants.extend(varFileParser.get_constants())
        except Exception as e:
            messagebox.showerror(
                title="Parsing Error",
                message=f"Error parsing variable files (.var):\n{str(e)}\n\nContinuing without constants."
            )
            # Continue without constants if parsing fails

        library.constants = constants

        # Generate CHM file of the library
        try:
            libraryToChm = LibraryDeclarationToChm(library=library)
            libraryToChm.generate_library_chm(build_folder=folder_path_build)
        except PermissionError:
            messagebox.showerror(
                title="Build Error",
                message=f"Permission denied when writing to build folder:\n{folder_path_build}\n\nPlease check folder permissions."
            )
            return
        except Exception as e:
            messagebox.showerror(
                title="Build Error",
                message=f"Error generating CHM help file:\n{str(e)}"
            )
            return

        library_folder_path_build = Path(folder_path_build).resolve() / library.name

        # Show infos (number of functions / function blocks, structures, enumerations, constants) in message box
        num_functions = len(library.functions)
        num_function_blocks = len(library.function_blocks)
        num_structures = len(library.structures)
        num_enumerations = len(library.enumerations)
        num_constants = len(library.constants)

        messagebox.showinfo(
            title="Information",
            message=f"Library build successfully in {library_folder_path_build.as_posix()}\n"
                    f"Library Version: {library.version}\n"
                    f"Library Type: {library.type if library.type else 'N/A'}\n"
                    f"Functions: {num_functions}\n"
                    f"Function Blocks: {num_function_blocks}\n"
                    f"Structures: {num_structures}\n"
                    f"Enumerations: {num_enumerations}\n"
                    f"Constants: {num_constants}"
        )

        open_build = messagebox.askyesno(
            title="Question",
            message="Would you open builded library folder?"
        )

        if not open_build:
            return

        # Open explorer to build folder
        try:
            subprocess.run(['explorer', normpath(library_folder_path_build.as_posix())])
        except Exception as e:
            messagebox.showerror(
                title="Error",
                message=f"Could not open build folder:\n{str(e)}"
            )




if __name__ == "__main__":
    root = tk.Tk()
    app = BRLibToMarkdownApp(root)
    root.mainloop()
