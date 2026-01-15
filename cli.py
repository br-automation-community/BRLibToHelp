"""Command-line interface for B&R Library to CHM Help generator.

This module provides CLI support for automated builds and CI/CD integration.
"""
import argparse
import sys
from pathlib import Path
from core import LibraryProcessor
from version import __version__


def parse_args():
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog='BRLibToHelp',
        description='Generate CHM help files from B&R Automation Studio libraries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --library C:\\Projects\\MyLib --output C:\\Build
  %(prog)s -l ./src/MyLibrary -o ./docs/help
  %(prog)s -l C:\\Libs\\MyLib -o C:\\Docs -k -v

Exit Codes:
  0 - Success
  1 - Invalid arguments
  2 - Library folder error
  3 - Output folder error
  4 - CHM generation failed
        """
    )
    
    parser.add_argument(
        '--library', '-l',
        required=True,
        metavar='PATH',
        help='Path to library folder containing .fun, .typ, .var files'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=False,
        metavar='PATH',
        help='Path to build output folder (optional: defaults to <library>/Help/)'
    )
    
    parser.add_argument(
        '--keep-sources', '-k',
        action='store_true',
        help='Keep HTML source files (only valid with --output argument)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output for debugging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for CLI interface.
    
    Returns:
        int: Exit code (0=success, >0=error)
    """
    args = parse_args()
    
    # Validate arguments
    if args.keep_sources and not args.output:
        print(f"[ERROR] --keep-sources requires --output to be specified", file=sys.stderr)
        print(f"   When no output folder is specified, CHM is placed in <library>/Help/ without sources", file=sys.stderr)
        return 1
    
    # Resolve library path
    lib_path = Path(args.library).resolve()
    
    # Determine output path
    if args.output:
        out_path = Path(args.output).resolve()
        use_help_folder = False
    else:
        # Use <library>/Help/ as default
        out_path = lib_path / "Help"
        use_help_folder = True
    
    if args.verbose:
        print(f"=== B&R Library to CHM Help Generator ===")
        print(f"   Library folder: {lib_path}")
        if use_help_folder:
            print(f"   Output: {out_path} (library Help folder)")
        else:
            print(f"   Output folder: {out_path}")
        print(f"   Keep sources: {'Yes' if args.keep_sources else 'No'}")
        print()
    
    # Validate library path exists
    if not lib_path.exists():
        print(f"[ERROR] Library folder not found", file=sys.stderr)
        print(f"   Path: {lib_path}", file=sys.stderr)
        return 2
    
    # Validate or create output path
    if args.output:
        # User-specified output must exist
        if not out_path.exists():
            print(f"[ERROR] Output folder not found", file=sys.stderr)
            print(f"   Path: {out_path}", file=sys.stderr)
            print(f"   Tip: Create the output directory before running", file=sys.stderr)
            return 3
    else:
        # Create Help folder if it doesn't exist
        if not out_path.exists():
            try:
                out_path.mkdir(parents=True)
                if args.verbose:
                    print(f"[INFO] Created Help folder: {out_path}")
            except Exception as e:
                print(f"[ERROR] Could not create Help folder", file=sys.stderr)
                print(f"   Path: {out_path}", file=sys.stderr)
                print(f"   Error: {str(e)}", file=sys.stderr)
                return 3
    
    # Create processor
    # When using Help folder, never keep sources (keep_sources forced to False)
    processor = LibraryProcessor(
        library_path=str(lib_path),
        output_path=str(out_path),
        keep_sources=args.keep_sources if not use_help_folder else False,
        use_help_folder=use_help_folder
    )
    
    # Process library
    if args.verbose:
        print("[INFO] Parsing library files...")
    
    result = processor.process()
    
    # Handle errors
    if not result['success']:
        print(f"[ERROR] {result['error']}", file=sys.stderr)
        
        # Determine appropriate exit code based on error message
        error_lower = result['error'].lower()
        if 'library folder' in error_lower or 'not found' in error_lower:
            return 2
        elif 'output folder' in error_lower or 'permission' in error_lower:
            return 3
        else:
            return 4
    
    # Success!
    library = result['library']
    stats = result['stats']
    chm_path = result['chm_path']
    
    if args.verbose:
        print()
        print("[SUCCESS] CHM help file generated successfully!")
        print()
        print(f"[INFO] Output: {chm_path}")
        print(f"[INFO] Library: {library.name} v{library.version}")
        if library.type:
            print(f"   Type: {library.type}")
        print()
        print("[INFO] Documentation Statistics:")
        print(f"   Functions: {stats['functions']}")
        print(f"   Function Blocks: {stats['function_blocks']}")
        print(f"   Structures: {stats['structures']}")
        print(f"   Enumerations: {stats['enumerations']}")
        print(f"   Constants: {stats['constants']}")
        
        if use_help_folder:
            print()
            print(f"[INFO] CHM placed in library Help folder (ready for F1 integration)")
        elif not args.keep_sources:
            print()
            print("[INFO] HTML source files deleted (use -k to keep them)")
    else:
        # Concise output for scripts
        print(f"[OK] CHM generated: {chm_path}")
        print(f"   {library.name} v{library.version} - "
              f"{stats['functions']} functions, "
              f"{stats['function_blocks']} FBs, "
              f"{stats['structures']} structs, "
              f"{stats['enumerations']} enums, "
              f"{stats['constants']} constants")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
