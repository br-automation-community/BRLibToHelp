# Introduction 
This python project is used to parse B&R Automation library from Automation Studio project and generate a CHM help file, it let generate sources and a .bat file to recompile it if modifications are made.

> [!NOTE]  
> If you add / remove html files you may have troubles trying to regenerate it from the .bat file. If you delete / add functions or function blocks please run again the python application.

It handle IEC and ANSI C libraries.
> [!WARNING]
> For ANSI C if there is header files in the library folder (.h) they are not parsed.

# Requirements
- Python 3.13.9 (only if running from source)

# Getting Started

## Option 1: Use the Executable (Recommended)

A pre-built executable is available in the [Releases](../../releases) section. No Python installation required!

1. Download `BRLibToHelp.exe` from the latest release
2. Run the executable directly
3. Use the GUI to select your library folder and generate CHM files

## Option 2: Run from Source

1.  Clone the repo
2.  Go in the directory `cd BrLibToMarkdown`
3.  Create new Python virtual environnement `python -m venv .venv`
4.  Activate the virtual environnement `./.venv/Scripts/activate`
5.  Install dependencies `python -p pip install -r ./requirements.txt`
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
├── Lib<LibraryName>.chm          # Main CHM file (copy this to Help/ folder)
├── build_Lib<LibraryName>.bat    # Batch file to rebuild CHM
├── hhc.exe                        # HTML Help Compiler
├── style.css                      # Styling
├── Gen/                           # General documentation
├── FBKs/                          # Functions and Function Blocks
└── DataTypes/                     # Structures, Enumerations, Constants
```

# Additionnal elements to add manually in html files
```html
<p class="tips">This is a "tips" example.</p>

<p class="important">This is an "important" example.</p>

<p class="demo">This is a "demo" example.</p>

<p class="redundancy">This is a "redundancy" example.</p>
```
![Additionnal classes](/images/AdditionnalClasses.png)