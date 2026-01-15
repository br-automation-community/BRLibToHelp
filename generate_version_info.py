"""Generate version_info.txt for PyInstaller from version.py

This script reads version.py and generates a Windows version info file
that PyInstaller uses to embed metadata in the executable.

Usage:
    python generate_version_info.py
"""
from version import __version__, __author__, __description__
from pathlib import Path

def generate_version_info():
    """Generate version_info.txt file for PyInstaller."""
    
    # Parse version string (e.g., "1.0.0" -> (1, 0, 0, 0))
    version_parts = __version__.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    
    file_version = ', '.join(version_parts[:4])
    file_version_tuple = f"({', '.join(version_parts[:4])})"
    
    version_info_content = f"""# UTF-8
#
# Auto-generated from version.py
# DO NOT EDIT MANUALLY - Run generate_version_info.py instead
#
# For more details about fixed file info:
# See: https://msdn.microsoft.com/en-us/library/ms646997.aspx

VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={file_version_tuple},
    prodvers={file_version_tuple},
    # Contains a bitmask that specifies the valid bits 'flags'
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{__author__}'),
        StringStruct(u'FileDescription', u'{__description__}'),
        StringStruct(u'FileVersion', u'{__version__}'),
        StringStruct(u'InternalName', u'BRLibToHelp'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2026 {__author__}'),
        StringStruct(u'OriginalFilename', u'BRLibToHelp.exe'),
        StringStruct(u'ProductName', u'BRLibToHelp'),
        StringStruct(u'ProductVersion', u'{__version__}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    # Write to file
    output_file = Path(__file__).parent / "version_info.txt"
    output_file.write_text(version_info_content, encoding='utf-8')
    
    print(f"[OK] Generated version_info.txt")
    print(f"   Version: {__version__}")
    print(f"   Author: {__author__}")
    print(f"   Description: {__description__}")

if __name__ == "__main__":
    generate_version_info()
