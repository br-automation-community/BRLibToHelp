"""Main entry point for B&R Library to CHM Help Application.

This module initializes and launches the Tkinter GUI application.
"""
import tkinter as tk
from hmi import BRLibToMarkdownApp


def main():
    """Initialize and run the main application."""
    root = tk.Tk()
    app = BRLibToMarkdownApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()