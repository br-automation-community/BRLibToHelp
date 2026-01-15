"""Main entry point for B&R Library to CHM Help Application.

This module initializes and launches either the GUI or CLI interface
based on command-line arguments.
"""
import sys

def main():
    """Initialize and run the application in GUI or CLI mode."""
    # If command-line arguments are provided, use CLI mode
    if len(sys.argv) > 1:
        # CLI mode - keep console visible
        from cli import main as cli_main
        sys.exit(cli_main())
    
    # Import Tkinter only in GUI mode (lazy import to avoid triggering runw.exe bootloader)
    import tkinter as tk
    from hmi import BRLibToMarkdownApp
    
    root = tk.Tk()
    app = BRLibToMarkdownApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()