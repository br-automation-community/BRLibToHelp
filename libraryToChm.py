from datatypes import Library, Function, FunctionBlock, VarInput, VarOutput, Structure, Enumeration, VarConstant
from pathlib import Path
from typing import List
import subprocess
import html
import shutil
from htmlGenerator import FunctionBlockHtmlGenerator


class LibraryDeclarationToChm():
    def __init__(self, library: Library) -> None:
        self.library: Library = library
        self.hhc_compiler_path = Path("./bin/hhc.exe")
        self.html_generator = FunctionBlockHtmlGenerator()

    def generate_library_chm(self, build_folder: str = "./build/") -> str:
        """Generate CHM file for the library and return the path to the generated .chm file.
        
        Uses B&R Automation Studio folder structure (directly in CHM folder):
        - FBKs/: Function blocks and Functions
        - DataTypes/: Structures, Enumerations, Constants
        - Gen/: General documentation (index page)
        - Samples/: Sample code (optional)
        """
        # Build folder structure: build/<LibraryName>/chm/
        path_build_folder = Path(build_folder) / self.library.name / "chm"
        if not path_build_folder.exists():
            path_build_folder.mkdir(parents=True)
        
        # HTML files are directly in the CHM folder (no library name subfolder)
        lib_folder = path_build_folder
        
        # Copy CSS file to the CHM folder
        self.copy_css_file(lib_folder)
        
        # Copy hhc.exe and create .bat file to root CHM folder
        self.copy_hhc_and_create_bat(path_build_folder)
        
        # Create HTML files for all content
        html_files = []
        
        # Create "Gen" folder for general documentation (index page)
        gen_folder = lib_folder / "Gen"
        if not gen_folder.exists():
            gen_folder.mkdir(parents=True)
        
        # Generate index/home page in Gen folder
        index_file = self.generate_index_page(gen_folder)
        html_files.append(index_file)
        
        # Create "FBKs" folder for Function blocks and Functions
        fbks_folder = lib_folder / "FBKs"
        
        # Generate functions and function blocks index
        if self.library.functions or self.library.function_blocks:
            fb_index_file = self.generate_functions_and_fbs_index(fbks_folder, self.library.functions, self.library.function_blocks)
            html_files.append(fb_index_file)
        
        # Generate functions - each function gets its own HTML file directly in FBKs folder
        for func in self.library.functions:
            if func is not None:
                func_file = self.generate_function_file(fbks_folder, func)
                html_files.append(func_file)
        
        # Generate function blocks - each FB gets its own HTML file directly in FBKs folder
        for fb in self.library.function_blocks:
            if fb is not None:
                fb_file = self.generate_function_block_file(fbks_folder, fb)
                html_files.append(fb_file)
        
        # Create "DataTypes" folder for data types and constants
        datatypes_folder = lib_folder / "DataTypes"
        if not datatypes_folder.exists():
            datatypes_folder.mkdir(parents=True)
        
        # Generate Data types and constants index
        dt_index_file = self.generate_data_types_and_constants_index(datatypes_folder)
        html_files.append(dt_index_file)
        
        # Generate structures
        if self.library.structures:
            struct_index_file = self.generate_structures_index(datatypes_folder, self.library.structures)
            html_files.append(struct_index_file)
            for struct in self.library.structures:
                if struct is not None:
                    struct_file = self.generate_structure_file(datatypes_folder, struct)
                    html_files.append(struct_file)
        
        # Generate enumerations
        if self.library.enumerations:
            enum_index_file = self.generate_enumerations_index(datatypes_folder, self.library.enumerations)
            html_files.append(enum_index_file)
            for enum in self.library.enumerations:
                if enum is not None:
                    enum_file = self.generate_enumeration_file(datatypes_folder, enum)
                    html_files.append(enum_file)
        
        # Generate constants
        if self.library.constants:
            const_file = self.generate_constants_file(datatypes_folder, self.library.constants)
            html_files.append(const_file)
        
        # Create "Samples" folder (optional - for future use)
        samples_folder = lib_folder / "Samples"
        if not samples_folder.exists():
            samples_folder.mkdir(parents=True)
        
        # Generate CHM project files (in the root CHM folder, not in the library subfolder)
        hhp_file = self.generate_hhp_file(path_build_folder, html_files, lib_folder)
        hhc_file = self.generate_hhc_file(path_build_folder)
        hhk_file = self.generate_hhk_file(path_build_folder)
        
        # Compile CHM
        chm_file = self.compile_chm(hhp_file, path_build_folder)
        
        return str(chm_file)

    def generate_index_page(self, build_folder: Path, css_path: str = "../style.css") -> Path:
        """Generate the main index/home page for the CHM in the Gen folder."""
        html_file = build_folder / "index.html"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{html.escape(self.library.name)} - Library Documentation</title>
    <link rel="stylesheet" type="text/css" href="{css_path}">
</head>
<body>
    <h1>{html.escape(self.library.name)}</h1>
    
    <div class="section">
        <h2>Library Contents</h2>
        <ul>
            <li><a href="../FBKs/FBKs.html">Functions and Function Blocks</a></li>
            <li><a href="../DataTypes/DataTypes.html">Data types and constants</a></li>
        </ul>
    </div>
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file
    
    def copy_css_file(self, build_folder: Path) -> Path:
        """Copy the style.css file to the build folder."""
        # Source CSS file
        css_source = Path(__file__).parent / "css" / "style.css"
        
        # Destination CSS file
        css_dest = build_folder / "style.css"
        
        # Copy the file
        shutil.copy2(css_source, css_dest)
        
        return css_dest

    def copy_hhc_and_create_bat(self, build_folder: Path) -> tuple[Path, Path]:
        """Copy hhc.exe to the build folder and create a .bat file to rebuild the CHM.
        
        Returns:
            tuple: (Path to copied hhc.exe, Path to created .bat file)
        """
        # Copy hhc.exe to build folder
        hhc_source = Path(__file__).parent / "bin" / "hhc.exe"
        hhc_dest = build_folder / "hhc.exe"
        
        if hhc_source.exists():
            shutil.copy2(hhc_source, hhc_dest)
        else:
            raise FileNotFoundError(f"hhc.exe not found at {hhc_source}")
        
        # Create .bat file to rebuild the CHM
        bat_file = build_folder / f"build_Lib{self.library.name}.bat"
        hhp_filename = f"Lib{self.library.name}.hhp"
        chm_filename = f"Lib{self.library.name}.chm"
        
        bat_content = f"""@echo off
REM Batch file to rebuild {chm_filename}
REM Generated automatically by BRLibToMarkdown

echo Building {chm_filename}...
hhc.exe "{hhp_filename}"

REM Note: hhc.exe returns 1 on success, so we check for the output file
if exist "{chm_filename}" (
    echo.
    echo Success! CHM file created: {chm_filename}
    exit /b 0
) else (
    echo.
    echo Error: CHM file was not created
    exit /b 1
)
"""
        
        with open(bat_file, "w", encoding='utf-8') as f:
            f.write(bat_content)
        
        return hhc_dest, bat_file

    def is_user_defined_type(self, type_name: str) -> bool:
        """Check if a type is a user-defined type (structure or enumeration).
        
        Args:
            type_name: The type name to check (may include ARRAY OF, POINTER TO, etc.)
        
        Returns:
            bool: True if the type is user-defined, False otherwise
        """
        # Extract the base type name, removing ARRAY OF, POINTER TO, etc.
        base_type = type_name.strip()
        
        # Remove common prefixes
        prefixes_to_remove = ["POINTER TO ", "REFERENCE TO ", "ARRAY [", "ARRAY OF "]
        for prefix in prefixes_to_remove:
            if base_type.upper().startswith(prefix.upper()):
                base_type = base_type[len(prefix):].strip()
        
        # Remove array dimensions if present
        if '[' in base_type:
            base_type = base_type.split('[')[0].strip()
        
        # Check if it's in structures
        for struct in self.library.structures:
            if struct.name == base_type:
                return True
        
        # Check if it's in enumerations
        for enum in self.library.enumerations:
            if enum.name == base_type:
                return True
        
        return False

    def get_type_link(self, type_name: str, relative_path: str) -> str:
        """Get the HTML link for a user-defined type, or just the escaped type name if not user-defined.
        Also creates links for constants used in array dimensions.
        
        Args:
            type_name: The type name
            relative_path: Relative path from current HTML file to the root of the CHM build
        
        Returns:
            str: HTML string with link if user-defined, or escaped type name otherwise
        """
        # Extract the base type and any decorators
        original_type = type_name.strip()
        base_type = original_type
        prefix = ""
        array_dimensions = ""
        suffix = ""
        
        # Handle POINTER TO
        if base_type.upper().startswith("POINTER TO "):
            prefix = "Pointer to "
            base_type = base_type[11:].strip()
        
        # Handle REFERENCE TO
        if base_type.upper().startswith("REFERENCE TO "):
            prefix = "Reference to "
            base_type = base_type[13:].strip()
        
        # Handle ARRAY OF
        if base_type.upper().startswith("ARRAY OF "):
            prefix = prefix + "Array of "
            base_type = base_type[9:].strip()
        
        # Handle ARRAY [dimensions] OF type
        if 'ARRAY [' in base_type.upper() or 'ARRAY[' in base_type.upper():
            # Extract array dimensions
            array_start_idx = base_type.upper().index('ARRAY')
            # Find the opening bracket
            bracket_start = base_type.index('[', array_start_idx)
            bracket_count = 1
            bracket_end = bracket_start + 1
            
            # Find matching closing bracket
            while bracket_count > 0 and bracket_end < len(base_type):
                if base_type[bracket_end] == '[':
                    bracket_count += 1
                elif base_type[bracket_end] == ']':
                    bracket_count -= 1
                bracket_end += 1
            
            # Extract the array dimensions part
            array_dimensions_raw = base_type[bracket_start:bracket_end]
            
            # Process constants in array dimensions
            array_dimensions = self.link_constants_in_text(array_dimensions_raw, relative_path)
            
            # Find OF keyword
            remaining = base_type[bracket_end:].strip()
            if remaining.upper().startswith('OF '):
                prefix = prefix + "Array " + array_dimensions + " of "
                base_type = remaining[3:].strip()
            else:
                # No OF found, the whole thing might be the type
                prefix = prefix + "Array " + array_dimensions + " "
                base_type = remaining.strip()
        
        # Check if base type is user-defined
        is_structure = False
        is_enumeration = False
        
        for struct in self.library.structures:
            if struct.name == base_type:
                is_structure = True
                break
        
        if not is_structure:
            for enum in self.library.enumerations:
                if enum.name == base_type:
                    is_enumeration = True
                    break
        
        # Generate link if user-defined
        if is_structure:
            link = f"{relative_path}DataTypes/Structures/{html.escape(base_type)}.html"
            return f"{prefix}<a href=\"{link}\">{html.escape(base_type)}</a>{html.escape(suffix)}"
        elif is_enumeration:
            link = f"{relative_path}DataTypes/Enumerations/{html.escape(base_type)}.html"
            return f"{prefix}<a href=\"{link}\">{html.escape(base_type)}</a>{html.escape(suffix)}"
        else:
            # Process any constants in the base type as well (in case there are expressions)
            base_type_with_links = self.link_constants_in_text(base_type, relative_path)
            return f"{prefix}{base_type_with_links}{html.escape(suffix)}"

    def link_constants_in_text(self, text: str, relative_path: str) -> str:
        """Replace constant names in text with links to the constants page.
        
        Args:
            text: Text that may contain constant names
            relative_path: Relative path from current HTML file to the CHM root
            
        Returns:
            str: Text with constant names replaced by HTML links, properly escaped
        """
        if not self.library.constants:
            return html.escape(text)
        
        # Build a list of constant names sorted by length (longest first to avoid partial matches)
        constant_names = sorted([const.name for const in self.library.constants], key=len, reverse=True)
        
        import re
        replacements = []
        
        # Find all occurrences of constants in the text
        for const_name in constant_names:
            # Use word boundary matching
            pattern = r'\b' + re.escape(const_name) + r'\b'
            
            for match in re.finditer(pattern, text):
                start = match.start()
                end = match.end()
                # Check if this position is not already part of a replacement
                overlaps = False
                for existing_start, existing_end, _ in replacements:
                    if not (end <= existing_start or start >= existing_end):
                        overlaps = True
                        break
                
                if not overlaps:
                    replacements.append((start, end, const_name))
        
        # If no replacements, just escape and return
        if not replacements:
            return html.escape(text)
        
        # Sort replacements by position
        replacements.sort(key=lambda x: x[0])
        
        # Build result by processing text in segments
        result = ""
        last_pos = 0
        
        for start, end, const_name in replacements:
            # Add escaped text before the constant
            result += html.escape(text[last_pos:start])
            
            # Add the linked constant
            link = f"{relative_path}DataTypes/Constants/Constants.html"
            result += f'<a href="{link}#{html.escape(const_name)}">{html.escape(const_name)}</a>'
            
            last_pos = end
        
        # Add any remaining text after the last replacement
        result += html.escape(text[last_pos:])
        
        return result

    def generate_function_file(self, build_folder: Path, func: Function) -> Path:
        """Generate an HTML file for a function directly in the FBKs folder."""
        if not build_folder.exists():
            build_folder.mkdir(parents=True)
        html_file = build_folder / f"{func.name}.html"
        
        # Calculate relative path to CSS from this HTML file (FBKs folder is one level below root)
        css_relative_path = "../style.css"
        # Relative path to root for type links
        relative_path_to_root = "../"
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(self.generate_html_content(func, "Function", css_relative_path, relative_path_to_root))
        
        return html_file

    def generate_function_block_file(self, build_folder: Path, fb: FunctionBlock) -> Path:
        """Generate an HTML file for a function block directly in the FBKs folder."""
        if not build_folder.exists():
            build_folder.mkdir(parents=True)
        html_file = build_folder / f"{fb.name}.html"
        
        # Calculate relative path to CSS from this HTML file (FBKs folder is one level below root)
        css_relative_path = "../style.css"
        # Relative path to root for type links
        relative_path_to_root = "../"
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(self.generate_html_content(fb, "Function block", css_relative_path, relative_path_to_root))
        
        return html_file

    def generate_html_content(self, fb: Function | FunctionBlock, pou_type: str, css_path: str = "style.css", relative_path_to_root: str = "../") -> str:
        """Generate HTML content for a function or function block.
        
        Args:
            fb: Function or FunctionBlock to generate HTML for
            pou_type: Type description ("Function" or "Function block")
            css_path: Relative path to the CSS file from this HTML file
            relative_path_to_root: Relative path to the CHM root folder for type links
        """
        description = html.escape(fb.description) if fb.description else ""
        
        # Get the function block diagram HTML
        fub_diagram = self.html_generator.generate_fub_diagram_html(fb)
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{html.escape(fb.name)}</title>
    <link rel="stylesheet" type="text/css" href="{css_path}">
</head>
<body>
    <h1>{html.escape(fb.name)}</h1>
    
    
    <p>{description}</p>
    
    <h2>{pou_type}</h2>
    <div class="section1">
        {fub_diagram}
    </div>
    
    <h2>Interface</h2>
    {self.generate_html_table_variables(fb, relative_path_to_root)}
    
</body>
</html>"""
        
        return html_content

    def generate_html_table_variables(self, fb: Function | FunctionBlock, relative_path_to_root: str = "../") -> str:
        """Generate HTML table for function/function block variables.
        
        Args:
            fb: Function or FunctionBlock to generate table for
            relative_path_to_root: Relative path from the HTML file to the CHM root folder
        """
        html_table = """<table id="tableWithOption" class="parameter_tab" border="1">
    <thead>
        <tr>
            <th class="auto-style1">
                <div align="center"><b>I/O</b></div>
            </th>
            <th class="parameter_tab">
                <div align="center"><b>Parameter</b></div>
            </th>
            <th class="parameter_tab">
                <div align="center"><b>Data type</b></div>
            </th>
            <th class="parameter_tab">
                <div align="center"><b>Description</b></div>
            </th>
        </tr>
    </thead>
    <tbody>
"""
        
        for var in fb.var_input:
            html_table += self.generate_html_table_row(var, relative_path_to_root)
        
        if isinstance(fb, FunctionBlock):
            for var in fb.var_output:
                html_table += self.generate_html_table_row(var, relative_path_to_root)
        for var in fb.var_in_out:
            html_table += self.generate_html_table_row(var, relative_path_to_root)
        
        html_table += """    </tbody>
</table>"""
        
        return html_table

    def generate_html_table_row(self, var: VarInput | VarOutput, relative_path_to_root: str = "../") -> str:
        """Generate a single HTML table row for a variable.
        
        Args:
            var: Variable to generate row for
            relative_path_to_root: Relative path from the HTML file to the CHM root folder
        """
        if var.is_reference:
            var_type = f"Pointer to {var.type}"
        else:
            var_type = str(var.type)
        
        # Generate link for user-defined types
        var_type_html = self.get_type_link(var_type, relative_path_to_root)
        
        comment = html.escape(var.comment1) if var.comment1 else ""
        
        return f"""        <tr>
            <td valign="TOP" class="auto-style1">{html.escape(var.I_O)}</td>
            <td valign="TOP" class="parameter_tab">{html.escape(var.name)}</td>
            <td valign="TOP" class="parameter_tab">{var_type_html}</td>
            <td valign="TOP" class="parameter_tab">{comment}</td>
        </tr>
"""

    def generate_functions_and_fbs_index(self, build_folder: Path, functions: List[Function], function_blocks: List[FunctionBlock]) -> Path:
        """Generate an index HTML file for functions and function blocks in FBKs folder."""
        if not build_folder.exists():
            build_folder.mkdir(parents=True)
        html_file = build_folder / "FBKs.html"
        
        # Calculate relative path to CSS (FBKs folder is one level below root)
        css_relative_path = "../style.css"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Functions and Function Blocks</title>
    <link rel="stylesheet" type="text/css" href="{css_relative_path}">
</head>
<body>
    <h1>Functions and Function Blocks</h1>
    
"""
        
        # Functions section
        if functions:
            html_content += """
    <h2>Functions</h2>
    <table class="parameter_tab" border="1">
        <thead>
            <tr>
                <th class="parameter_tab">
                    <div align="center"><b>Function</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Description</b></div>
                </th>
            </tr>
        </thead>
        <tbody>
"""
            for func in functions:
                description = html.escape(func.description.replace('\n', ' ').strip()) if func.description else ""
                # Link directly to the HTML file in same folder (FBKs)
                html_content += f"""            <tr>
                <td valign="TOP" class="parameter_tab"><a href="{html.escape(func.name)}.html">{html.escape(func.name)}</a></td>
                <td valign="TOP" class="parameter_tab">{description}</td>
            </tr>
"""
            html_content += """        </tbody>
    </table>
"""
        
        # Function Blocks section
        if function_blocks:
            html_content += """
    <h2>Function Blocks</h2>
    <table class="parameter_tab" border="1">
        <thead>
            <tr>
                <th class="parameter_tab">
                    <div align="center"><b>Function Block</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Description</b></div>
                </th>
            </tr>
        </thead>
        <tbody>
"""
            for fb in function_blocks:
                description = html.escape(fb.description.replace('\n', ' ').strip()) if fb.description else ""
                # Link directly to the HTML file in same folder (FBKs)
                html_content += f"""            <tr>
                <td valign="TOP" class="parameter_tab"><a href="{html.escape(fb.name)}.html">{html.escape(fb.name)}</a></td>
                <td valign="TOP" class="parameter_tab">{description}</td>
            </tr>
"""
            html_content += """        </tbody>
    </table>
"""
        
        html_content += """
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_data_types_and_constants_index(self, build_folder: Path) -> Path:
        """Generate index HTML file for data types and constants in DataTypes folder."""
        if not build_folder.exists():
            build_folder.mkdir(parents=True)
        html_file = build_folder / "DataTypes.html"
        
        # Calculate relative path to CSS (DataTypes folder is one level below root)
        css_relative_path = "../style.css"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Data types and constants</title>
    <link rel="stylesheet" type="text/css" href="{css_relative_path}">
</head>
<body>
    <h1>Data types and constants</h1>

    <h2>Contents</h2>
    <ul>
"""
        if len(self.library.structures) > 0:
            html_content += """        <li><a href="Structures/Structures.html">Structures</a></li>"""
        if len(self.library.enumerations) > 0:
            html_content += """        <li><a href="Enumerations/Enumerations.html">Enumerations</a></li>"""
        if len(self.library.constants) > 0:
            html_content += """        <li><a href="Constants/Constants.html">Constants</a></li>"""
        html_content += """
    </ul>
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_structures_index(self, build_folder: Path, structures: List[Structure]) -> Path:
        """Generate index HTML file for structures."""
        folder_path = build_folder / "Structures"
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
        html_file = folder_path / "Structures.html"
        
        # Calculate relative path to CSS
        css_relative_path = "../../style.css"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Structures</title>
    <link rel="stylesheet" type="text/css" href="{css_relative_path}">
</head>
<body>
    <h1>Structures</h1>
    
    
    <table class="parameter_tab" border="1">
        <thead>
            <tr>
                <th class="parameter_tab">
                    <div align="center"><b>Structure</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Description</b></div>
                </th>
            </tr>
        </thead>
        <tbody>
"""
        
        for struct in structures:
            member_count = len(struct.members)
            html_content += f"""            <tr>
                <td valign="TOP" class="parameter_tab"><a href="{html.escape(struct.name)}.html">{html.escape(struct.name)}</a></td>
                <td valign="TOP" class="parameter_tab"></td>
            </tr>
"""
        
        html_content += """        </tbody>
    </table>
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_structure_file(self, build_folder: Path, struct: Structure) -> Path:
        """Generate HTML file for a single structure."""
        folder_path = build_folder / "Structures"
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
        html_file = folder_path / f"{struct.name}.html"
        
        # Calculate relative path to CSS
        css_relative_path = "../../style.css"
        
        # Add description if available
        description_html = ""
        if struct.description:
            description_html = f"    <p>{html.escape(struct.description)}</p>\n    \n"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{html.escape(struct.name)}</title>
    <link rel="stylesheet" type="text/css" href="{css_relative_path}">
</head>
<body>
    <h1>{html.escape(struct.name)}</h1>
    {description_html}

    <h2>Members</h2>

    <table class="parameter_tab" border="1">
        <thead>
            <tr>
                <th class="parameter_tab">
                    <div align="center"><b>Member</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Data type</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Description</b></div>
                </th>
            </tr>
        </thead>
        <tbody>
"""
        
        for member in struct.members:
            # Generate link for user-defined types
            member_type_html = self.get_type_link(str(member.type), "../../")
            comment = html.escape(member.comment1) if member.comment1 else ""
            html_content += f"""            <tr>
                <td valign="TOP" class="parameter_tab">{html.escape(member.name)}</td>
                <td valign="TOP" class="parameter_tab">{member_type_html}</td>
                <td valign="TOP" class="parameter_tab">{comment}</td>
            </tr>
"""
        
        html_content += """        </tbody>
    </table>
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_enumerations_index(self, build_folder: Path, enumerations: List[Enumeration]) -> Path:
        """Generate index HTML file for enumerations."""
        folder_path = build_folder / "Enumerations"
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
        html_file = folder_path / "Enumerations.html"
        
        # Calculate relative path to CSS
        css_relative_path = "../../style.css"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Enumerations</title>
    <link rel="stylesheet" type="text/css" href="{css_relative_path}">
</head>
<body>
    <h1>Enumerations</h1>
    
    
    <table class="parameter_tab" border="1">
        <thead>
            <tr>
                <th class="parameter_tab">
                    <div align="center"><b>Enumeration</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Default Value</b></div>
                </th>
            </tr>
        </thead>
        <tbody>
"""
        
        for enum in enumerations:
            literal_count = len(enum.literals)
            default_val = html.escape(enum.default_value) if enum.default_value else ""
            html_content += f"""            <tr>
                <td valign="TOP" class="parameter_tab"><a href="{html.escape(enum.name)}.html">{html.escape(enum.name)}</a></td>
                <td valign="TOP" class="parameter_tab">{default_val}</td>
            </tr>
"""
        
        html_content += """        </tbody>
    </table>
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_enumeration_file(self, build_folder: Path, enum: Enumeration) -> Path:
        """Generate HTML file for a single enumeration."""
        folder_path = build_folder / "Enumerations"
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
        html_file = folder_path / f"{enum.name}.html"
        
        # Calculate relative path to CSS
        css_relative_path = "../../style.css"
        
        # Add description if available
        description_html = ""
        if enum.description:
            description_html = f"    <p>{html.escape(enum.description)}</p>\n    \n"

        default_value_html = ""
        if enum.default_value:
            default_value_html = f"<p><strong>Default value:</strong> <code>{html.escape(enum.default_value)}</code></p>"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{html.escape(enum.name)}</title>
    <link rel="stylesheet" type="text/css" href="{css_relative_path}">
</head>
<body>
    <h1>{html.escape(enum.name)}</h1>
    {description_html}
    
    <h2>Literals</h2>
    
    <h3>Default value: {default_value_html}</h3>

    <table class="parameter_tab" border="1">
        <thead>
            <tr>
                <th class="parameter_tab">
                    <div align="center"><b>Literal</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Value</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Description</b></div>
                </th>
            </tr>
        </thead>
        <tbody>
"""
        
        for literal in enum.literals:
            value = html.escape(literal.value) if literal.value else ""
            comment = html.escape(literal.comment1) if literal.comment1 else ""
            html_content += f"""            <tr>
                <td valign="TOP" class="parameter_tab">{html.escape(literal.name)}</td>
                <td valign="TOP" class="parameter_tab">{value}</td>
                <td valign="TOP" class="parameter_tab">{comment}</td>
            </tr>
"""
        
        html_content += """        </tbody>
    </table>
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_constants_file(self, build_folder: Path, constants: List[VarConstant]) -> Path:
        """Generate HTML file for all constants."""
        folder_path = build_folder / "Constants"
        if not folder_path.exists():
            folder_path.mkdir(parents=True)
        html_file = folder_path / "Constants.html"
        
        # Calculate relative path to CSS
        css_relative_path = "../../style.css"
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Constants</title>
    <link rel="stylesheet" type="text/css" href="{css_relative_path}">
</head>
<body>
    <h1>Constants</h1>
    
    
    <h2>Library Constants</h2>
    
    <table class="parameter_tab" border="1">
        <thead>
            <tr>
                <th class="parameter_tab">
                    <div align="center"><b>Name</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Data type</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Value</b></div>
                </th>
                <th class="parameter_tab">
                    <div align="center"><b>Description</b></div>
                </th>
            </tr>
        </thead>
        <tbody>
"""
        
        for const in constants:
            const_type = html.escape(str(const.type))
            value = html.escape(const.default_value) if const.default_value else ""
            comment = html.escape(const.comment1) if const.comment1 else ""
            # Add an anchor for each constant so links can jump to it
            html_content += f"""            <tr id="{html.escape(const.name)}">
                <td valign="TOP" class="parameter_tab"><a name="{html.escape(const.name)}"></a>{html.escape(const.name)}</td>
                <td valign="TOP" class="parameter_tab">{const_type}</td>
                <td valign="TOP" class="parameter_tab">{value}</td>
                <td valign="TOP" class="parameter_tab">{comment}</td>
            </tr>
"""
        
        html_content += """        </tbody>
    </table>
</body>
</html>"""
        
        with open(html_file, "w", encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file

    def generate_hhp_file(self, build_folder: Path, html_files: List[Path], lib_folder: Path) -> Path:
        """Generate HTML Help Project (.hhp) file with 'Lib' prefix for CHM file.
        
        Args:
            build_folder: Root CHM build folder
            html_files: List of all HTML files to include
            lib_folder: Library subfolder containing all content
        """
        hhp_file = build_folder / f"Lib{self.library.name}.hhp"
        
        # Convert file paths to relative paths from build_folder
        relative_files = []
        for file in html_files:
            try:
                rel_path = file.relative_to(build_folder)
                relative_files.append(str(rel_path).replace('\\', '/'))
            except ValueError:
                # If file is not relative to build_folder, skip it
                continue
        
        # Add the CSS file (in library subfolder)
        css_file = lib_folder / "style.css"
        if css_file.exists():
            try:
                rel_css = css_file.relative_to(build_folder)
                relative_files.append(str(rel_css).replace('\\', '/'))
            except ValueError:
                pass
        
        hhp_content = f"""[OPTIONS]
Compatibility=1.1 or later
Compiled file=Lib{self.library.name}.chm
Contents file=Lib{self.library.name}.hhc
Default topic=Gen/index.html
Display compile progress=No
Index file=Lib{self.library.name}.hhk
Language=0x409 English (United States)
Title={self.library.name} - Library Documentation

[FILES]
"""
        
        for file in relative_files:
            hhp_content += f"{file}\n"
        
        hhp_content += """
[INFOTYPES]
"""
        
        with open(hhp_file, "w", encoding='utf-8') as f:
            f.write(hhp_content)
        
        return hhp_file

    def generate_hhc_file(self, build_folder: Path) -> Path:
        """Generate HTML Help Contents (.hhc) file - table of contents with 'Lib' prefix.
        
        Structure:
        - General (index.html)
        - FBKs and Functions (folder containing all functions and function blocks)
        - Data types and constants (folder containing structures, enums, constants)
        """
        hhc_file = build_folder / f"Lib{self.library.name}.hhc"
        
        hhc_content = f"""<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<HTML>
<HEAD>
<meta name="GENERATOR" content="Microsoft&reg; HTML Help Workshop 4.1">
<!-- Sitemap 1.0 -->
</HEAD><BODY>
<OBJECT type="text/site properties">
    <param name="ImageType" value="Folder">
</OBJECT>
<UL>
    <LI> <OBJECT type="text/sitemap">
        <param name="Name" value="General">
        <param name="Local" value="Gen/index.html">
        </OBJECT>
"""
        
        # Functions and Function Blocks section - single folder with all FBs and Functions
        if self.library.functions or self.library.function_blocks:
            hhc_content += f"""    <LI> <OBJECT type="text/sitemap">
        <param name="Name" value="FBKs and Functions">
        <param name="Local" value="FBKs/FBKs.html">
        </OBJECT>
        <UL>
"""
            
            # Add all functions directly under "FBKs and Functions"
            for func in self.library.functions:
                if func is not None:
                    hhc_content += f"""            <LI> <OBJECT type="text/sitemap">
                <param name="Name" value="{html.escape(func.name)}">
                <param name="Local" value="FBKs/{html.escape(func.name)}.html">
                </OBJECT>
"""
            
            # Add all function blocks directly under "FBKs and Functions"
            for fb in self.library.function_blocks:
                if fb is not None:
                    hhc_content += f"""            <LI> <OBJECT type="text/sitemap">
                <param name="Name" value="{html.escape(fb.name)}">
                <param name="Local" value="FBKs/{html.escape(fb.name)}.html">
                </OBJECT>
"""
            
            hhc_content += """        </UL>
"""
        
        # Data types and constants section
        hhc_content += f"""    <LI> <OBJECT type="text/sitemap">
        <param name="Name" value="Data types and constants">
        <param name="Local" value="DataTypes/DataTypes.html">
        </OBJECT>
        <UL>
"""
        
        # Structures
        if self.library.structures:
            hhc_content += f"""            <LI> <OBJECT type="text/sitemap">
                <param name="Name" value="Structures">
                <param name="Local" value="DataTypes/Structures/Structures.html">
                </OBJECT>
                <UL>
"""
            for struct in self.library.structures:
                if struct is not None:
                    hhc_content += f"""                    <LI> <OBJECT type="text/sitemap">
                        <param name="Name" value="{html.escape(struct.name)}">
                        <param name="Local" value="DataTypes/Structures/{html.escape(struct.name)}.html">
                        </OBJECT>
"""
            hhc_content += """                </UL>
"""
        
        # Enumerations
        if self.library.enumerations:
            hhc_content += f"""            <LI> <OBJECT type="text/sitemap">
                <param name="Name" value="Enumerations">
                <param name="Local" value="DataTypes/Enumerations/Enumerations.html">
                </OBJECT>
                <UL>
"""
            for enum in self.library.enumerations:
                if enum is not None:
                    hhc_content += f"""                    <LI> <OBJECT type="text/sitemap">
                        <param name="Name" value="{html.escape(enum.name)}">
                        <param name="Local" value="DataTypes/Enumerations/{html.escape(enum.name)}.html">
                        </OBJECT>
"""
            hhc_content += """                </UL>
"""
        
        # Constants
        if self.library.constants:
            hhc_content += f"""            <LI> <OBJECT type="text/sitemap">
                <param name="Name" value="Constants">
                <param name="Local" value="DataTypes/Constants/Constants.html">
                </OBJECT>
"""
        
        hhc_content += """        </UL>
</UL>
</BODY></HTML>
"""
        
        with open(hhc_file, "w", encoding='utf-8') as f:
            f.write(hhc_content)
        
        return hhc_file

    def generate_hhk_file(self, build_folder: Path) -> Path:
        """Generate HTML Help Index (.hhk) file - keyword index with 'Lib' prefix."""
        hhk_file = build_folder / f"Lib{self.library.name}.hhk"
        
        hhk_content = """<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<HTML>
<HEAD>
<meta name="GENERATOR" content="Microsoft&reg; HTML Help Workshop 4.1">
<!-- Sitemap 1.0 -->
</HEAD><BODY>
<UL>
"""
        
        # Add functions to index
        for func in self.library.functions:
            if func is not None:
                hhk_content += f"""    <LI> <OBJECT type="text/sitemap">
        <param name="Name" value="{html.escape(func.name)}">
        <param name="Local" value="FBKs/{html.escape(func.name)}.html">
        </OBJECT>
"""
        
        # Add function blocks to index
        for fb in self.library.function_blocks:
            if fb is not None:
                hhk_content += f"""    <LI> <OBJECT type="text/sitemap">
        <param name="Name" value="{html.escape(fb.name)}">
        <param name="Local" value="FBKs/{html.escape(fb.name)}.html">
        </OBJECT>
"""
        
        # Add structures to index
        for struct in self.library.structures:
            if struct is not None:
                hhk_content += f"""    <LI> <OBJECT type="text/sitemap">
        <param name="Name" value="{html.escape(struct.name)}">
        <param name="Local" value="DataTypes/Structures/{html.escape(struct.name)}.html">
        </OBJECT>
"""
        
        # Add enumerations to index
        for enum in self.library.enumerations:
            if enum is not None:
                hhk_content += f"""    <LI> <OBJECT type="text/sitemap">
        <param name="Name" value="{html.escape(enum.name)}">
        <param name="Local" value="DataTypes/Enumerations/{html.escape(enum.name)}.html">
        </OBJECT>
"""
        
        hhk_content += """</UL>
</BODY></HTML>
"""
        
        with open(hhk_file, "w", encoding='utf-8') as f:
            f.write(hhk_content)
        
        return hhk_file

    def compile_chm(self, hhp_file: Path, build_folder: Path) -> Path:
        """Compile the CHM file using hhc.exe with 'Lib' prefix."""
        if not self.hhc_compiler_path.exists():
            raise FileNotFoundError(f"HTML Help Compiler not found at {self.hhc_compiler_path}")
        
        # hhc.exe returns 1 on success and 0 on failure (opposite of normal)
        # So we need to handle this specially
        try:
            result = subprocess.run(
                [str(self.hhc_compiler_path.absolute()), str(hhp_file.absolute())],
                cwd=str(build_folder.absolute()),
                capture_output=True,
                text=True
            )
            
            # Check if CHM file was created (with 'Lib' prefix)
            chm_file = build_folder / f"Lib{self.library.name}.chm"
            if chm_file.exists():
                return chm_file
            else:
                raise RuntimeError(f"CHM compilation failed. Return code: {result.returncode}\n"
                                 f"STDOUT: {result.stdout}\n"
                                 f"STDERR: {result.stderr}")
        
        except Exception as e:
            raise RuntimeError(f"Error compiling CHM: {str(e)}")
