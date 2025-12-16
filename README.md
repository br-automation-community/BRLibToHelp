# Introduction 
This python project is used to parse B&R Automation library from Automation Studio project and generate a CHM help file, it let generate sources and a .bat file to recompile it if modifications are made.

> [!NOTE]  
> If you add / remove html files you may have troubles trying to regenerate it from the .bat file. If you delete / add functions or function blocks please run again the python application.

It handle IEC and ANSI C libraries.
> [!WARNING]
> For ANSI C if there is header files in the library folder (.h) they are not parsed.

# Requirements
- Python 3.13.9

# Getting Started
1.  Clone the repo
2.  Go in the directory `cd BrLibToMarkdown`
3.  Create new Python virtual environnement `python -m venv .venv`
4.  Activate the virtual environnement `./.venv/Scripts/activate`
5.  Install dependencies `python -p pip install -r ./requirements.txt`

# Additionnal elements to add manually in html files
```html
<p class="tips">This is a "tips" example.</p>

<p class="important">This is an "important" example.</p>

<p class="demo">This is a "demo" example.</p>

<p class="redundancy">This is a "redundancy" example.</p>
```
![Additionnal classes](/images/AdditionnalClasses.png)