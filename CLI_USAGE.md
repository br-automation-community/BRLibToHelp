# Command-Line Interface Usage

## Overview

BRLibToHelp now supports command-line interface (CLI) mode for automation and CI/CD integration.

## Quick Start

### Display Help
```bash
BRLibToHelp.exe --help
```

### Help Folder Mode (Recommended for F1 Integration)
```bash
# Places CHM in <library>/Help/Lib<LibraryName>.chm
BRLibToHelp.exe --library "C:\Path\To\Library"

# Same with verbose output
BRLibToHelp.exe -l "C:\MyLib" -v
```

### Custom Output Mode
```bash
# Generate to custom folder (CHM will be in <output>/<LibraryName>/chm/)
BRLibToHelp.exe --library "C:\Path\To\Library" --output "C:\Build"

# Keep HTML sources for manual editing
BRLibToHelp.exe -l "C:\MyLib" -o "C:\Build" --keep-sources

# Verbose output
BRLibToHelp.exe -l "C:\MyLib" -o "C:\Build" -v
```

## Command-Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--library` | `-l` | Yes | - | Path to library folder (.fun, .typ, .var files) |
| `--output` | `-o` | No | `<library>/Help/` | Path to build output folder (CHM will be in `<output>/<LibraryName>/chm/`) |
| `--keep-sources` | `-k` | No | false | Keep HTML sources (only with --output) |
| `--verbose` | `-v` | No | false | Enable verbose output |
| `--help` | `-h` | No | - | Show help message |
| `--version` | | No | - | Show version number |

## Behavior Differences

### Help Folder Mode (no --output)
- **Target**: Places CHM directly in `<library>/Help/`
- **Creates**: Help folder if it doesn't exist
- **Keeps**: Only the CHM file (`Lib<LibraryName>.chm`)
- **Deletes**: All temporary build files, HTML sources, CSS
- **Note**: `--keep-sources` is not allowed (returns error)
- **Use case**: Direct F1 integration in Automation Studio

### Custom Output Mode (with --output)
- **Target**: Places files in specified output folder
- **Structure**: CHM file will be located at `<output>/<LibraryName>/chm/Lib<LibraryName>.chm`
- **Default**: Generates CHM only, deletes HTML sources
- **With -k**: Keeps all HTML sources, CSS, and rebuild script

### GUI Mode (no arguments)
- **Default**: Generates CHM and keeps all HTML sources
- Same behavior as previous versions

## Exit Codes

- `0` - Success
- `1` - Invalid command-line arguments
- `2` - Library folder not found or invalid
- `3` - Output folder not found or access error
- `4` - CHM compilation failed

## Testing

### Test CLI Help
```bash
BRLibToHelp.exe --help
```

### Test Invalid Arguments
```bash
# Should exit with code 2
BRLibToHelp.exe --library "NonExistentFolder" --output "C:\Build"

# Should exit with code 3
BRLibToHelp.exe --library "C:\ValidLib" --output "NonExistentFolder"
```

### Test Verbose Output
```bash
# Help folder mode
BRLibToHelp.exe -l "C:\MyLib" -v

# Custom output mode
BRLibToHelp.exe -l "C:\MyLib" -o "C:\Build" -v
```

### Test Keep Sources
```bash
# Should work
BRLibToHelp.exe -l "C:\MyLib" -o "C:\Build" -k

# Should fail (error: --keep-sources requires --output)
BRLibToHelp.exe -l "C:\MyLib" -k
```

## Notes

- The GUI remains the default when running `BRLibToHelp.exe` without arguments
- CLI mode is automatically activated when any command-line arguments are provided
- In CLI mode, HTML sources are deleted by default to save space (use `-k` to keep them)
- In GUI mode, all sources are always kept for manual editing and rebuilding
