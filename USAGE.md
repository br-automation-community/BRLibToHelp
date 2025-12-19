# BRLibToHelp - Usage Guide

This guide demonstrates how to use BRLibToHelp to generate CHM help files for your B&R Automation Studio libraries.

## Table of Contents
- [Running the Application](#running-the-application)
- [Generating CHM Help Files](#generating-chm-help-files)
- [Installing the Help File](#installing-the-help-file)
- [Using F1 Context Help](#using-f1-context-help)
- [Modifying and Rebuilding](#modifying-and-rebuilding)

---

## Running the Application

### Launching BRLibToHelp

Double-click `BRLibToHelp.exe` to launch the application. The main window will appear with two folder selection fields and control buttons.

![Application Launch](images/gifs/launch_application.gif)

---

## Generating CHM Help Files

### Step 1: Select Library Folder

Click the **Browse** button next to "Library folder path" and navigate to your B&R library folder. The library folder should contain:
- A `.fun` file (function/function block declarations)
- Optional `.typ` files (structures and enumerations)
- Optional `.var` files (constants)

![Select Library Folder](images/gifs/select_library_folder.gif)

### Step 2: Select Build Output Folder

Click the **Browse** button next to "Build folder path" and choose where you want the CHM file and source files to be generated.

![Select Build Folder](images/gifs/select_build_folder.gif)

### Step 3: Generate the Documentation

Once both paths are selected, the **Start** button becomes enabled. Click **Start** to begin the generation process.

The application will:
1. Parse all library files
2. Generate HTML documentation
3. Compile the CHM file
4. Display a summary

![Generate Documentation](images/gifs/generate_documentation.gif)

---

## Troubleshooting

### F1 Help Not Working

**Checklist:**
- ✅ CHM file is in the `Help/` folder inside your library
- ✅ CHM filename matches pattern: `Lib<LibraryName>.chm`
- ✅ Library is properly added to your Automation Studio project
- ✅ CHM file has been unblocked (see above)
- ✅ Element name is selected when pressing F1

---

## Tips and Best Practices

### Documentation Maintenance

1. **Version Control**: Keep CHM files in sync with library versions
2. **Update Regularly**: Regenerate documentation when functions/FBs change
3. **Test F1 Help**: Verify key functions have working help before release
4. **Meaningful Descriptions**: Add comments in your source code - they appear in the help

### Custom Styling

You can add special CSS classes to HTML files for enhanced documentation:

```html
<p class="tips">Useful tip information</p>
<p class="important">Critical information</p>
<p class="demo">Demo or example content</p>
<p class="redundancy">Redundancy-related information</p>
```

![Additional CSS Classes](images/AdditionnalClasses.png)

---

## Summary

You've learned how to:
- ✅ Generate CHM help files from B&R libraries
- ✅ Install help files for F1 integration
- ✅ Use context-sensitive help in Automation Studio
- ✅ Edit and rebuild documentation
- ✅ Troubleshoot common issues

---

**Need Help?** Open an issue on GitHub or consult the B&R Automation Studio documentation.
