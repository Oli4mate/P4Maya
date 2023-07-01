<h1 align="center">
<b>P4Maya for Maya2023</b><br>
Beta version 0.1
</h1>

**<h3>Tool installation</h3>**
1. In the '**P4Maya for Maya2023**' folder, there should be 2 folders: '**TOOl**' and '**P4**'. One of these is the tool, and the other is the [Official P4Python API from Helix Core](https://www.perforce.com/manuals/p4python/Content/P4Python/Home-p4python.html).
2. Put contents of the '**P4**' folder (the '**P4.py**' and '**P4API.py**' files) into the ***Maya Python site-extensions folder***, found at: 
```
Maya2023 Install Location (usually Program Files/Autodesk/Maya2023) / Python / Lib / site-packages
```
3. Put contents of the '**TOOL**' folder ('**P4Maya**' folder and '**userSetup.py**' file) into the ***Maya scripts folder***, found at:
```
Documents / Maya / scripts
```
4. Open Maya, and run the following Python script in the script editor:
```py
import P4Maya.Install as I

I.run()
```
5. Enter your Perforce server, user, and workspace information.
6. Done! The tool is now ready to use.

<br><br>

**<h3>User Guide</h3>**
* ***Startup Script*** - The script that runs on start-up does 4 things:
    1. If you do not have Perforce settings set up, you will be prompted to do so.
    2. If you do not have the latest version of the file, you will be prompted if you want to get the latest version.
    3. If you do not have the file checked out, you will be prompted if you want to check it out.
    4. If you have the file checked out, it will initialise the '*Auto-Shelving*' feature saves and auto-shelves the file to Perforce every 10 minutes. This ensures that your latest WIP file is always in the cloud so you have a decreased chance of losing work. An additional benefit is that other Perforce users can see your latest work by seeing your auto-shelved file.
* ***File Status*** - This shows the Perforce status of the file: Up-to-date, Outdated, Checkout by you, Checkout by other user, Perforce Absence. This shelf button also functions as a reload for the current file status.
* ***Get Latest*** - This will get the latest version of the file from Perforce, and re-open the file.
* ***Submit*** - This will prompt you to give a changelist description, after which it will submit your changelist if you have one.
* ***Checkout*** - This will create a new changelist and check out your file.
* ***Revert*** - This will prompt you how you want to revert; '*Revert All*' or '*Revert Unchanged*', after which it will revert with the selected method.
* ***Open Shelved*** - This will open the latest auto-shelved version of your file.
* ***P4Maya Settings*** - This is where you can set up your Perforce connection settings.

<br><br>

**<h3>Version History</h3>**
***July 1st 2023 - Beta 0.1***
* First release of the tool!
* Added all basic functionality for checking out, submitting, reverting (changed and unchanged), file syncing (getting latest), and file status visual.
* Added additional functionality for *auto-shelfing* feature, which saves and auto-shelves the file to Perforce every 10 minutes. The goal here is to ensure that your latest WIP file is always in the cloud so you have a decreased chance of losing work. An additional benefit is that other Perforce users can see your latest work by seeing your auto-shelved file.

<br><br>

**<h3>License</h3>**
The contents of the 'TOOL' folder (excluding the contents of the 'icons' folder) fall under the Creative Commons CC BY-SA license.

The contents of the 'P4' folder are Copyright (c) 2023, Perforce Software, Inc. All rights reserved.