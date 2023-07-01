### P4Maya for Maya2023
### by Olivier Dral
###
### Beta version 0.1
### 1-7-2023
### 
### For any issues, please reach out to me at oli4dral@gmail.com.


# INSTALL SCRIPT FOR CREATING THE SHELF AND SHELF ITEMS

def run():
    import maya.cmds as cmds
    import maya.mel as mel
    import os

    # create new shelf
    gShelfTopLevel = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
    currentShelf = cmds.tabLayout(gShelfTopLevel,q=1,st=1)
    shelf = cmds.shelfLayout("P4Maya")

    # get icons folder
    iconsPath = os.getenv("MAYA_APP_DIR") + "/scripts/P4Maya/icons/"

    # status button and update it
    cmds.shelfButton("P4FileStatus",
                    label = "P4FileStatus",
                    annotation = "Perforce File Status",
                    image1 = iconsPath + "p4v_outdated.png",
                    command = """import P4Maya.P4Commands as P4

P4.UpdateStatusIcon()""",
                    parent = shelf)

    # separator
    mel.eval("addShelfSeparator()")

    # get latest button
    cmds.shelfButton("GetLatest",
                    label = "GetLatest",
                    annotation = "Get Latest",
                    image1 = iconsPath + "getlatest.png",
                    command = """import P4Maya.P4Commands as P4

P4.GetLatest()""",
                    parent = shelf)

    # submit button
    cmds.shelfButton("Submit",
                    label = "Submit",
                    annotation = "Submit",
                    image1 = iconsPath + "submit.png",
                    command = """import P4Maya.P4Commands as P4

P4.Submit()""",
                    parent = shelf)

    # separator
    mel.eval("addShelfSeparator()")

    # checkout button
    cmds.shelfButton("Checkout",
                    label = "Checkout",
                    annotation = "Checkout",
                    image1 = iconsPath + "checkout.png",
                    command = """import P4Maya.P4Commands as P4

P4.Checkout()""",
                    parent = shelf)

    # revert button
    cmds.shelfButton("Revert",
                    label = "Revert",
                    annotation = "Revert",
                    image1 = iconsPath + "revert.png",
                    command = """import P4Maya.P4Commands as P4

P4.Revert()""",
                    parent = shelf)

    # separator
    mel.eval("addShelfSeparator()")

    # open shelved button
    cmds.shelfButton("OpenShelved",
                    label = "OpenShelved",
                    annotation = "Open Shelved",
                    image1 = iconsPath + "openshelved.png",
                    command = """import P4Maya.P4Commands as P4

P4.OpenShelfed()""",
                    parent = shelf)

    # separator
    mel.eval("addShelfSeparator()")

    # settings button
    cmds.shelfButton("P4MayaSettings",
                    label = "P4MayaSettings",
                    annotation = "P4Maya Settings",
                    image1 = iconsPath + "settings.png",
                    command = """import P4Maya.P4Commands as P4

P4.SettingMenu()""",
                    parent = shelf)

    # run updates and settings
    import P4Maya.P4Commands as P4Maya
    P4Maya.SettingMenu()

    shelfpath = os.getenv("MAYA_APP_DIR") + "/2023/prefs/shelves/shelf_P4Maya"
    cmds.saveShelf(shelf,shelfpath)

    print("P4Maya installed!")