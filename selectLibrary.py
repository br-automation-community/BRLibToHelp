from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import os

class SelectLibrary():
    def __init__(self, library_path:str = "") -> None:
        self.library_path = library_path
        if self.library_path == "":
            self.ask_directory()
        self.validate_library_path()
        self.library_declaration_path = self.get_library_declaration_path()


    def ask_directory(self) -> None:
        root: tk.Tk = tk.Tk()
        root.wm_attributes('-topmost', 1)
        root.withdraw()

        selected_directory = filedialog.askdirectory(parent=root ,title="Please choose library directory",)
        if selected_directory:
            self.library_path = selected_directory
        else:
            raise Exception("User cancel directory selection")

    
    def validate_library_path(self) -> bool:
        library_path = Path(self.library_path)
        if not library_path.exists():
            raise FileNotFoundError
        return True
        
    def get_library_path(self) -> str:
        return self.library_path

    def get_library_declaration_path(self) -> str:
        fun_files = [each for each in os.listdir(self.library_path) if each.endswith('.fun')]
        if len(fun_files) > 1:
            raise Exception("Library can only have 1 .fun file for declaration")
        if len(fun_files) == 0:
            raise Exception("No .fun file found in library directory")
        return fun_files[0]
    
    def get_types_declaration_paths(self) -> str:
        ''' Search for all .typ files in the library directory and child directories and return their paths as a list of strings
        '''
        type_files = []
        for root, dirs, files in os.walk(self.library_path):
            for name in files:
                if name.endswith('.typ'):
                    type_files.append(os.path.join(root, name))
        return type_files

    def get_variable_declaration_paths(self) -> str:
        ''' Search for all .var files in the library directory and child directories and return their paths as a list of strings
        '''
        var_files = []
        for root, dirs, files in os.walk(self.library_path):
            for name in files:
                if name.endswith('.var'):
                    var_files.append(os.path.join(root, name))
        return var_files