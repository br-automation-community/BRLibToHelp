import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import List
from parser import LibraryDeclarationFileParser, TypeFileParser, VarFileParser
from selectLibrary import SelectLibrary
from libraryToChm import LibraryDeclarationToChm
from datatypes import Structure, Enumeration, VarConstant
import subprocess
from os.path import normpath

class BRLibToMarkdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("B&R Lib to Markdown App")

        # Library folder path
        self.folder_path_library_label = tk.Label(root, text="Library folder path:")
        self.folder_path_library_label.grid(row=0, column=0, padx=10, pady=10)

        self.folder_path_library_entry = tk.Entry(root, width=50)
        self.folder_path_library_entry.grid(row=0, column=1, padx=10, pady=10)
        self.folder_path_library_entry.config(state="readonly")

        self.folder_path_library_button = tk.Button(root, text="Browse", command=self.browse_folder_library)
        self.folder_path_library_button.grid(row=0, column=2, padx=10, pady=10)

        # Build folder path
        self.folder_path_build_label = tk.Label(root, text="Build folder path:")
        self.folder_path_build_label.grid(row=1, column=0, padx=10, pady=10)

        self.folder_path_build_entry = tk.Entry(root, width=50)
        self.folder_path_build_entry.grid(row=1, column=1, padx=10, pady=10)
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
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_library_entry.config(state="normal")
            self.folder_path_library_entry.delete(0, tk.END)
            self.folder_path_library_entry.insert(0, folder_selected)
            self.folder_path_library_entry.config(state="readonly")
        self.start_is_valid()

    def browse_folder_build(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path_build_entry.config(state="normal")
            self.folder_path_build_entry.delete(0, tk.END)
            self.folder_path_build_entry.insert(0, folder_selected)
            self.folder_path_build_entry.config(state="readonly")
        self.start_is_valid()


    def start_is_valid(self) -> None:
        if self.folder_path_are_valid():
            self.start_button.config(state="normal")
        else:
            self.start_button.config(state="disabled")

    def folder_path_are_valid(self) -> bool:
        folder_path_library = self.folder_path_library_entry.get()
        folder_path_build = self.folder_path_build_entry.get()
        if folder_path_build != "" and folder_path_library != "":
            library_path = Path(self.folder_path_library_entry.get())
            build_path = Path(self.folder_path_build_entry.get())
            return library_path.exists() and build_path.exists()
        return False

    def start(self):
        folder_path_library = self.folder_path_library_entry.get()
        folder_path_build = self.folder_path_build_entry.get()
        select_lib = SelectLibrary(folder_path_library)

        lib_declaration_path = Path(folder_path_library).resolve() / select_lib.get_library_declaration_path()
        type_file_paths = select_lib.get_types_declaration_paths()
        var_file_paths = select_lib.get_variable_declaration_paths()
        structures: List[Structure] = []
        enumerations: List[Enumeration] = []
        constants: List[VarConstant] = []

        

        libFileParser = LibraryDeclarationFileParser()
        libFileParser.parse_fun_file(file_path=lib_declaration_path.as_posix())
        library = libFileParser.get_library()
        
        # Parse all types files in library folder
        for file_path in type_file_paths:
            typeFileParser = TypeFileParser()
            typeFileParser.parse_typ_file(file_path=file_path)
            structures.extend(typeFileParser.get_structures())
            enumerations.extend(typeFileParser.get_enumerations())
            
        library.structures = structures
        library.enumerations = enumerations
        
        # Parse all variable files in library folder
        for file_path in var_file_paths:
            varFileParser = VarFileParser()
            varFileParser.parse_var_file(file_path=file_path)
            constants.extend(varFileParser.get_constants())

        library.constants = constants

        # Generate CHM file of the library
        libraryToChm = LibraryDeclarationToChm(library=library)
        libraryToChm.generate_library_chm(build_folder=folder_path_build)

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
        subprocess.run(['explorer', normpath(library_folder_path_build.as_posix())])




if __name__ == "__main__":
    root = tk.Tk()
    app = BRLibToMarkdownApp(root)
    root.mainloop()
