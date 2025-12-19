# Introduction 
This python project is used to parse B&R Automation library from Automation Studio project and generate a CHM help file. It generates sources and a .bat file to recompile it if modifications are made.

> [!NOTE]  
> If you add / remove html files you may have troubles trying to regenerate it from the .bat file. If you delete / add functions or function blocks please run again the python application.

It handles IEC and ANSI C libraries.
> [!WARNING]
> For ANSI C, if there are header files in the library folder (.h) they are not parsed.

# Requirements
- Python 3.13.9 (only if running from source)

# Getting Started

## Option 1: Use the Executable (Recommended)

A pre-built executable is available in the [Releases](../../releases) section. No Python installation required!

1. Download `BRLibToHelp.exe` from the latest release
2. Run the executable directly
3. Use the GUI to select your library folder and generate CHM files

**📖 For detailed usage instructions with screenshots, see the [Usage Guide](USAGE.md)**

## Option 2: Run from Source

1.  Clone the repo
2.  Go in the directory `cd BRLibToHelp`
3.  Create new Python virtual environment `python -m venv .venv`
4.  Activate the virtual environment `./.venv/Scripts/activate`
5.  Install dependencies `pip install -r ./requirements.txt`
6.  Run the application: `python main.py`

# Using the Generated CHM Help File

## Integration with B&R Automation Studio

To enable F1 context-sensitive help in Automation Studio:

1. **Create a Help folder** in your library directory:
   ```
   <YourLibrary>/
   ├── <YourLibrary>.fun
   ├── <YourLibrary>.typ
   ├── <YourLibrary>.var
   └── Help/                    # Create this folder
       └── Lib<YourLibrary>.chm # Place your generated CHM file here
   ```

2. **Naming convention**: The CHM file must be named `Lib<YourLibraryName>.chm`
   - Example: If your library is named `MyLibrary`, the file must be `LibMyLibrary.chm`

3. **Using F1 Help**:
   - Open your project in Automation Studio
   - In the Logical View, select any function or function block from your library
   - Press **F1**
   - The corresponding help page will open automatically

## Generated Files Structure

After running the application, you'll find in the build folder:
```
build/<LibraryName>/chm/
├── Lib<LibraryName>.chm           # Main CHM file (copy this to Help/ folder)
├── build_Lib<LibraryName>.bat     # Batch file to rebuild CHM
├── hhc.exe                        # HTML Help Compiler
├── *.dll                          # Required DLLs for HHC
├── style.css                      # Styling
├── Gen/                           # General documentation
├── FBKs/                          # Functions and Function Blocks
└── DataTypes/                     # Structures, Enumerations, Constants
```

# Customizing the Generated Documentation

## Additional HTML Classes for Enhanced Styling

You can manually enhance the generated HTML files with custom CSS classes for special content formatting:

### Available Classes

```html
<!-- For helpful tips and suggestions -->
<p class="tips">💡 Tip: Use this parameter to optimize performance.</p>

<!-- For critical warnings or important information -->
<p class="important">⚠️ Important: This function must be called in a cyclic task.</p>

<!-- For demo code or example usage -->
<p class="demo">📝 Demo: See example implementation in the samples folder.</p>

<!-- For redundancy system information -->
<p class="redundancy">🔄 Redundancy: This function block supports redundant systems.</p>
```

### Visual Result

These classes provide distinct visual styling to make important information stand out:

![Additional CSS Classes](images/AdditionnalClasses.png)

### How to Add Custom Content

1. Navigate to the generated HTML files in `build/<LibraryName>/chm/`
2. Open the desired HTML file in a text editor (e.g., Notepad++, VS Code)
3. Locate the section where you want to add the styled content
4. Insert the HTML with your chosen class
5. Save the file

### Example: Adding a Tip to a Function

```html
<h2>MC_MoveAbsolute</h2>
<p>Moves the axis to an absolute position.</p>

<!-- Add your custom tip here -->
<p class="tips">💡 Tip: For optimal motion, ensure acceleration and deceleration values are properly configured.</p>

<h3>Parameters</h3>
<!-- ... rest of the documentation ... -->
```

> [!IMPORTANT]
> **After modifying HTML files, you must rebuild the CHM file:**
> 1. Navigate to `build/<LibraryName>/chm/`
> 2. Double-click `build_Lib<LibraryName>.bat`
> 3. Wait for compilation to complete
> 4. The updated `Lib<LibraryName>.chm` file will contain your changes
>
> **Note:** If you add/remove entire HTML files or change the structure, regenerate the documentation using the main application instead of the rebuild script.

> [!WARNING]
> **All manual modifications will be lost if you regenerate the documentation!**
> 
> If you run the BRLibToHelp application again on the same library:
> - All HTML files will be regenerated from scratch
> - Any custom content you added (tips, warnings, examples) will be **permanently deleted**
> - You will need to manually re-add your customizations
> 
> **Best Practices:**
> - Keep a backup copy of your customized HTML files
> - Document your customizations in a separate file for easy re-application
> - Only regenerate when library structure changes (new functions, changed parameters)
> - Use the rebuild batch file for minor HTML tweaks instead of full regeneration