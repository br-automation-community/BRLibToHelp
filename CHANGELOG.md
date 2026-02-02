# Changelog

All notable changes to this project will be documented in this file.

## [1.0.2] - 2026-02-02

### Added
- **Range-Constrained Type Support** 🎯
  - New `RangeType` dataclass for types with range constraints (e.g., `UDINT(1..9)`, `INT(MIN..MAX)`)
  - Full parsing support in structures, function blocks, and functions
  - Proper display in HTML documentation with format `TYPE(lower..upper)`
  - Support for both numeric literals and named constants as range bounds

- **Automatic Constant Hyperlinking** 🔗
  - Constants used in type definitions now automatically link to their definitions
  - Range types: `UDINT(MIN_VALUE..MAX_VALUE)` → clickable links to constants
  - Array dimensions: `ARRAY[0..MAX_SIZE]` → already supported, now consistent
  - String lengths: `STRING[MAX_LENGTH]` → clickable link when using constants
  - Links point to constant definitions in DataTypes/Constants section

### Changed
- **Enhanced Type Parser**
  - Updated variable declaration regex to capture parentheses in type names
  - Pattern now includes `()` characters: `[\w\s\[\]\.,\(\)]+`
  - Prevents skipping of range-constrained variable declarations

- **Improved Type Link Generation**
  - Extended `get_type_link()` method to detect and process range types
  - Automatic constant name extraction and link generation in range expressions
  - Support for mixed constant and literal bounds (e.g., `INT(0..MAX)`)

### Fixed
- Variables with range-constrained types no longer ignored in structures (Issue #5)
- Range type syntax now properly displayed in documentation (Issue #6)
- Constants in range bounds now properly hyperlinked (Issue #7)


## [1.0.1] - 2026-01-20

### Fixed
- Update message formatting in the library build success notification

## [1.0.0] - 2026-01-15

### Added
- **Centralized Version Management** 🏷️
  - New `version.py` file as single source of truth for version number
  - Version displayed in GUI window title: "B&R Lib to CHM Help - v1.0.0"
  - Version label at bottom of GUI window
  - CLI `--version` flag uses centralized version
  - Executable metadata (Windows properties) includes version info
  - Auto-generation of `version_info.txt` for PyInstaller
  - `generate_version_info.py` script for version info generation

- **Command-Line Interface (CLI) Support** 🚀
  - Full CLI mode for automation and CI/CD integration
  - **Help Folder Mode**: `--library <path>` (no output) places CHM in `<library>/Help/`
  - **Custom Output Mode**: `--library <path> --output <path>` for flexible output
  - Arguments: `--library` (required), `--output` (optional), `--keep-sources`, `--verbose`
  - Proper exit codes (0=success, 1-4=various errors)
  - Automatic mode detection (CLI with args, GUI without args)
  - Clean output for scripting (concise mode) and debugging (verbose mode)

- **PyInstaller Executable CLI Support** 💻
  - Executable now supports both GUI and CLI modes in single binary
  - Uses `--console --hide-console hide-late` for proper terminal output
  - Console window automatically hidden in GUI mode
  - Modified `build_executable.bat` to use optimized PyInstaller settings

- **Improved Error Messages** 📍
  - Parser errors now include filename and line numbers
  - Format: `[WARNING] Failed to parse X in file 'path/file.typ' (lines 72-107): error message`
  - Easier debugging of problematic library files

- **New Core Architecture**
  - `core.py`: Standalone `LibraryProcessor` class for business logic
  - `cli.py`: Command-line interface implementation
  - Separation of concerns: GUI and CLI share the same processing logic
  - Print warnings for non-critical parsing errors in CLI mode

### Changed

- **Refactored GUI Code**
  - `hmi.py`: Simplified to use `LibraryProcessor` from `core.py`
  - Removed duplicate business logic
  - Cleaner error handling and user feedback

- **Main Entry Point**
  - `main.py`: Now routes to CLI or GUI based on command-line arguments
  - Backward compatible: GUI launches by default with no arguments

- **CHM Generator**
  - `libraryToChm.py`: Added `keep_sources` and `use_help_folder` parameters
  - New `_cleanup_sources()` method for selective file deletion

### Fixed
- **Enumeration Parser Bug** 🐛
  - Fixed false positive when "STRUCT" keyword appears in enumeration comments
  - Now uses regex to check actual syntax: `NAME : STRUCT` vs `NAME : (`
  - Prevents misclassification of enumerations containing structure-related comments
  - Example: `RandomEnumLiteral := 16#FFFF, (*Adresse de la structure parametres*)` no longer triggers structure parser

### Documentation
- Added `CLI_USAGE.md`: Complete CLI documentation with examples
- Added troubleshooting guide for CLI usage
- Updated architecture documentation

## Previous Releases

See commit history for changes in earlier versions.
