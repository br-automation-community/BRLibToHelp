"""GUI application for converting B&R Automation libraries to CHM help files.

This module provides a Tkinter-based graphical user interface that allows users to:
- Select a B&R library folder
- Choose a build output directory
- Generate CHM documentation from the library
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from selectLibrary import is_valid_library
import subprocess
from os.path import normpath
from utils import get_resource_path
from core import LibraryProcessor
from version import __version__

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
        self.root.title(f"B&R Lib to CHM Help - v{__version__}")
        
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
        
        # Version label at the bottom
        self.version_label = tk.Label(root, text=f"Version {__version__}", fg="gray", font=("Arial", 8))
        self.version_label.grid(row=4, column=0, columnspan=3, pady=(0, 10))

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
        
        This method uses the core LibraryProcessor to handle all business logic,
        then displays the results in the GUI.
        """
        folder_path_library = self.folder_path_library_entry.get()
        folder_path_build = self.folder_path_build_entry.get()
        
        # Create processor (GUI always keeps sources)
        processor = LibraryProcessor(
            library_path=folder_path_library,
            output_path=folder_path_build,
            keep_sources=True
        )
        
        # Process the library
        result = processor.process()
        
        # Handle errors
        if not result['success']:
            messagebox.showerror(
                title="Error",
                message=result['error']
            )
            return
        
        # Success - show summary
        library = result['library']
        stats = result['stats']
        chm_path = result['chm_path']
        library_folder_path_build = Path(folder_path_build).resolve() / library.name

        messagebox.showinfo(
            title="Information",
            message=f"Library build successfully in {library_folder_path_build.as_posix()}\n"
                    f"Library Version: {library.version}\n"
                    f"Library Type: {library.type if library.type else 'N/A'}\n"
                    f"Functions: {stats['functions']}\n"
                    f"Function Blocks: {stats['function_blocks']}\n"
                    f"Structures: {stats['structures']}\n"
                    f"Enumerations: {stats['enumerations']}\n"
                    f"Constants: {stats['constants']}"
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
                message=f"Could not open build folder:\\n{str(e)}"
            )




if __name__ == "__main__":
    root = tk.Tk()
    app = BRLibToMarkdownApp(root)
    root.mainloop()
