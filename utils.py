"""Utility functions for path management, especially for PyInstaller bundled executables."""
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """Get the absolute path to a resource, works for dev and for PyInstaller bundles.
    
    When PyInstaller creates an executable, it extracts files to a temporary folder.
    This function returns the correct path whether running in:
    - Development mode (script execution)
    - PyInstaller --onefile mode (_MEIPASS temporary folder)
    - PyInstaller --onedir mode (relative to executable)
    
    Args:
        relative_path: Path relative to the script/executable location (e.g., "css/style.css")
    
    Returns:
        Path: Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in normal Python environment
        base_path = Path(__file__).parent
    
    return base_path / relative_path
