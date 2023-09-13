### P4Maya for Maya2023
### by Olivier Dral
###
### Beta version 0.1
### 1-7-2023
### 
### For any issues, please reach out to me at oli4dral@gmail.com.


# P4 COMMANDS SCRIPT FOR EASY P4PYTHON USAGE


### GET FILE STATUS
def GetStatus(file):

    import P4
    import maya.cmds as cmds

    # initialize client and variables
    p4 = P4.P4()
    settings = GetSettings()
    if settings == None:
        cmds.warning("Perforce settings are not set")
        return ["Absent"]
    else:
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        returnval = None

        # connect to server
        p4.connect()

        # get server info
        info = p4.run_info()
        currentuser = info[0]['userName']

        # check if file exists in depot
        try:
            results = p4.run_filelog('-l',file)
            checked_out = p4.run_opened('-a',file)
            if len(checked_out):
                user = checked_out[0]['user']
                if user == currentuser:
                    returnval = ["Self", checked_out]
                else:
                    returnval = ["Other",user]
            else:
                try:
                    uptodate = p4.run_sync('-n',file)
                    returnval = ["Outdated"]
                except:
                    returnval = ["Updated"]

        # print warning if file not in depot
        except P4.P4Exception:
            returnval = ["Absent"]

        # disconnect from server
        p4.disconnect()

        return returnval



### UPDATE STATUS ICON
def UpdateStatusIcon():
    import os
    import maya.cmds as cmds

    # get current file
    currentFile = cmds.file(q=1,sn=1)

    # get file status
    if currentFile:
        status = GetStatus(currentFile)
        iconfile = ""
        tooltip = ""
        
        # set button settings
        if status[0] == "Updated":
            iconfile = "p4v_updated.png"
            tooltip = "File up to date"
        elif status[0] == "Self":
            iconfile = "p4v_self.png"
            tooltip = "File checked out"
        elif status[0] == "Other":
            iconfile = "p4v_other.png"
            tooltip = f"File checked out by {status[1]}"
        elif status[0] == "Outdated":
            iconfile = "p4v_outdated.png"
            tooltip = "File is outdated"
        elif status[0] == "Absent":
            iconfile = "p4v_absent.png"
            tooltip = "File is not on Perforce"
        
        # get icon
        mayaPath = os.environ['MAYA_APP_DIR']
        icon = os.path.join(mayaPath, "scripts/P4Maya/icons", iconfile)
        
        # get button
        buttons = cmds.shelfLayout("P4Maya", q=True, ca=True)
        targetButton = "P4FileStatus"
        for but in buttons:
            if "separator" not in but:
                if cmds.shelfButton(but, q=True, l=True) == targetButton:
                    cmds.shelfButton(but, e=1, i=icon, ann=tooltip)



### GET LATEST ON FILE
def GetLatest():
    import os
    import P4
    import maya.cmds as cmds

    # get current file
    currentFile = cmds.file(q=1,sn=1)

    # initialize client and variables
    p4 = P4.P4()
    settings = GetSettings()
    if settings == None:
        cmds.warning("Settings are not set")
    else:
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        # connect to server
        p4.connect()

        # get file status
        if currentFile:

            # try getting latest
            try:
                p4.run_sync(currentFile)

                # reload file
                cmds.file(currentFile, open=True, force=True)

            # if no update, then add to counter
            except P4.P4Exception:
                if len(p4.errors):
                    cmds.warning("File is not on Perforce")
                else:
                    cmds.warning("File is already up to date")

        # disconnect from the server
        p4.disconnect()

        UpdateStatusIcon()



### CHECKING OUT FILE
def Checkout():
    import P4
    import maya.cmds as cmds
    import os

    # get current file
    currentFile = cmds.file(q=1,sn=1)



    # initialize client and variables
    p4 = P4.P4()
    settings = GetSettings()
    if settings == None:
        cmds.warning("Settings are not set")
    else:
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        # connect to server
        p4.connect()

        # get server info
        info = p4.run_info()
        currentuser = info[0]['userName']

        # changelist description
        fileName = os.path.basename(currentFile)
        Description = f"P4Maya edit to {fileName} by {currentuser}."

        # check if file is on server
        try:
            checkfile = p4.run_files(currentFile)

            # check if file is checked out
            checked_out = p4.run_opened('-a',currentFile)
            if len(checked_out):

                # check if checked out by someone else
                user = checked_out[0]['user']
                if user == currentuser:
                    cmds.warning("You already have this file checked out")
                else:
                    cmds.warning(f"File is already checked out by {user}")

            # if file is not checked out
            else:
                
                # check out file
                p4.run_edit(currentFile)
                
                # create changelist
                change = p4.fetch_change()
                change["Description"] = Description
                ret = p4.save_change(change)
                changelist = ret[0].split(" ")[1]
                
                # move to new changelist
                p4.run_reopen('-c',changelist,checkfile[0]['depotFile'])

                EnableAutoShelf()
                AutoShelf()

        # throw warning if the file does not exist in the depot
        except P4.P4Exception:
            cmds.warning("File does not exist on Perforce")
    
        UpdateStatusIcon()

        # disconnect from server
        p4.disconnect()



### RUN THE FILE SUBMIT
def runSubmit(changelist,description,windowref):

    import P4
    import maya.cmds as cmds

    # initialize client and variables
    p4 = P4.P4()
    settings = GetSettings()
    if settings == None:
        cmds.warning("Settings are not set")
    else:
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        # connect to server
        p4.connect()

        # change description
        change = p4.fetch_change(changelist)
        change['Description'] = description
        p4.save_change(change)

        # submit files
        returnval = p4.run_submit('-c',changelist)

        # disconnect from server
        p4.disconnect()

        # print out submitted changelist
        changelist = returnval[0]['change']
        cmds.warning(f'Submitted changelist {changelist}')

        UpdateStatusIcon()

        DisableAutoShelf()

        cmds.deleteUI(windowref)



### CREATE THE SUBMIT WINDOW
def createSubmitWindow(changelist):
    
    import maya.cmds as cmds
    
    # create submit window
    win = cmds.window("P4Maya Submit",
                       w=400,
                       h=175,
                       s=0)
    layoutMain = cmds.columnLayout(adjustableColumn=1)
    
    # top text
    cmds.text(f"Please provide a description for changelist {changelist}",
              align="center",
              font="boldLabelFont",
              h=30)
    cmds.separator(h=10)
    cmds.rowLayout(nc=2)
    
    # submit type
    type = cmds.optionMenu(h=100,
                    w=80)
    cmds.menuItem(label='EDIT')
    cmds.menuItem(label='FIX')
    cmds.menuItem(label='ADD')
    cmds.menuItem(label='REMOVE')
    
    # submit description
    description = cmds.scrollField(h=100,w=320)
    
    # submit command
    def compileSubmit(a):
        typeText = cmds.optionMenu(type,q=1,v=1)
        descriptionText = cmds.scrollField(description,q=1,tx=1)
        changelistText = changelist
        descfull = f"# [{typeText}]\n{descriptionText}"
        runSubmit(changelistText,descfull,win)
    
    # buttons
    cmds.setParent("..")
    cmds.separator(h=10)
    cmds.rowLayout(nc=2,w=400)
    cmds.button("Submit",w=200,h=25,c=compileSubmit)
    cmds.button("Cancel",w=200,h=25,c="cmds.deleteUI('%s')" % win)
    
    # show window
    cmds.showWindow(win)



### PREPARE FILE SUBMIT
def Submit():
    
    import P4
    import maya.cmds as cmds

    # get current file
    currentFile = cmds.file(q=1,sn=1)

    # initialize client and variables
    p4 = P4.P4()
    settings = GetSettings()
    if settings == None:
        cmds.warning("Settings are not set")
    else:
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        # connect to the server
        p4.connect()

        # get file status
        filestatus = GetStatus(currentFile)
        if filestatus[0] == "Self":

            # save file
            cmds.file(s=1)

            # get changelist
            changelist = filestatus[1][0]['change']
            
            # create submit window
            createSubmitWindow(changelist)
        
        # warning if file is not checked out
        else:
            cmds.warning("File is not checked out by you")
        
        # disconnect from server
        p4.disconnect()
        
        # update icon
        UpdateStatusIcon()



### REVERT UNCHANGED
def Revert():
    
    import P4
    import maya.cmds as cmds

    # get current file
    currentFile = cmds.file(q=1,sn=1)

    # save file
    cmds.file(s=1)

    # initialize client and variables
    p4 = P4.P4()
    settings = GetSettings()
    if settings == None:
        cmds.warning("Settings are not set")
    else:
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        # check if file is checked out by user
        status = GetStatus(currentFile)
        if status[0] == "Self":

            # ask user which revert option
            revertConfirm = cmds.confirmDialog(t="P4Maya",
                                                m=f"File is not up to date, do you want to get latest?",
                                                button=['Revert All','Revert Unchanged'],
                                                defaultButton='Revert All',
                                                cancelButton='Revert Unchanged'
                                                )

            # if a choice was made
            if revertConfirm != "dismiss":

                # connect to server
                p4.connect()

                # get changelist
                changelist = status[1][0]['change']
                reload = 1
            
                # if user wants full revert
                if revertConfirm == "Revert All":
                    p4.run_revert(currentFile)

                # if user wants only revert unchanged
                elif revertConfirm == "Revert Unchanged":
                    revert = p4.run_revert('-a','-c',changelist)
                    if len(revert) == 1:
                        reload = 0
                
                # if the changelist is empty after revert, delete it
                change = p4.run_describe(changelist)
                if "depotFile" not in change:
                    p4.run_shelve('-d','-c',changelist)
                    p4.run_change('-d',changelist)

                    DisableAutoShelf()

                # disconnect from server
                p4.disconnect()
                
                # update icon
                UpdateStatusIcon()

                # reload file
                if reload > 0:
                    cmds.file(currentFile, open=True, force=True)
                
        else:
            cmds.warning("File not checked out by you")



### STARTUP SCRIPT
def StartupScript():
    import P4
    import os
    import maya.cmds as cmds



    # if settings exist, run
    settings = GetSettings()
    if settings != None:
        
        # initialize client and variables
        p4 = P4.P4()
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        # connect to server
        p4.connect()

        # get connection info
        info = p4.run_info()
        connectionUser = info[0]['userName']

        # get maya file location
        filepath = cmds.file(q=True, sn=True)

        # if file is saved already
        if filepath:
            
            iconfile = ""
            tooltip = ""

            # check if file exists in depot
            try:
                results = p4.run_filelog('-l',filepath)
                
                # see if file is checked out
                checkout = p4.run_opened('-a',filepath)
                if len(checkout):
                    
                    # check if file is checked out by someone else
                    checkoutUser = checkout[0]['user']
                    if checkoutUser != connectionUser:
                        cmds.confirmDialog(bgc=(0.3,0,0), t="P4Maya", m=f"File is checked out by {checkoutUser}.")
                        iconfile = "p4v_other.png"
                        tooltip = f"File checked out by {checkoutUser}"
                    else:
                        iconfile = "p4v_self.png"
                        tooltip = "File checked out"
                
                else:

                    # notify if file is outdated
                    try:
                        uptodate = p4.run_sync('-n',filepath)
                        iconfile = "p4v_outdated.png"
                        tooltip = "File is outdated"
                        updateConfirm = cmds.confirmDialog(t="P4Maya",
                                        m=f"File is not up to date, do you want to get latest?",
                                        button=['Yes','No'],
                                        defaultButton='Yes',
                                        cancelButton='No',
                                        dismissString='No')
                        
                        # get latest on file
                        if updateConfirm == "Yes":
                            p4.run_sync(filepath)

                            # reload file
                            cmds.file(filepath, open=True, force=True)
                            
                            iconfile = "p4v_updated.png"
                            tooltip = "File up to date"
                    
                    # notify if file is not checked out
                    except:
                        iconfile = "p4v_updated.png"
                        tooltip = "File up to date"

                        checkoutConfirm = cmds.confirmDialog(t="P4Maya",
                                        m=f"File is not checked out, do you want to check it out?",
                                        button=['Yes','No'],
                                        defaultButton='Yes',
                                        cancelButton='No',
                                        dismissString='No')
                        
                        # check out file
                        if checkoutConfirm == "Yes":
                            file = os.path.basename(filepath)
                            returnval = p4.run_edit(filepath)
                            change = p4.fetch_change()
                            change["Description"] = f"P4Maya edit to {file} by {connectionUser}."
                            ret = p4.save_change(change)
                            changelist = ret[0].split(" ")[1]
                            p4.run_reopen('-c',changelist,filepath)
                            
                            iconfile = "p4v_self.png"
                            tooltip = "File checked out"

                            AutoShelf()

            # print if file is not on perforce
            except:
                cmds.warning("File is not on Perforce.")
                iconfile = "p4v_absent.png"
                tooltip = "File is not on Perforce"
            
            # get icon
            mayaPath = os.environ['MAYA_APP_DIR']
            icon = os.path.join(mayaPath, "scripts/P4Maya/icons", iconfile)

            # set status button
            buttons = cmds.shelfLayout("P4Maya", q=True, ca=True)
            targetButton = "P4FileStatus"
            for but in buttons:
                if "separator" not in but:
                    if cmds.shelfButton(but, q=True, l=True) == targetButton:
                        cmds.shelfButton(but, e=1, i=icon, ann=tooltip)

        # disconnect from server
        p4.disconnect()
    
    # if settings are not set, set them
    else:
        SettingMenu()
    
    # update the status icon
    UpdateStatusIcon()

    # create script job for autosave
    cmds.scriptJob(event=["renderSetupAutoSave",AutoShelf])

    # turn on autosave if checked out
    filepath = cmds.file(q=True, sn=True)
    status = GetStatus(filepath)
    if status == "Self":
        EnableAutoShelf()
    else:
        DisableAutoShelf()



### DISABLE AUTOSHELF FEATURE
def DisableAutoShelf():
    import os
    import maya.cmds as cmds

    # turn off autosave
    cmds.autoSave(enable=0)



### ENABLE AUTOSHELF FEATURE
def EnableAutoShelf():
    import os
    import maya.cmds as cmds

    # get autosave location
    mayaPath = os.getenv("TEMP")
    fullPath = os.path.join(mayaPath,"P4Maya_autosave")

    # turn on autosave with correct settings
    cmds.autoSave(enable=1,
                interval=600,
                destination=1,
                folder=fullPath
                )



### AUTOSHELF
def AutoShelf():
    import P4
    import os
    import maya.cmds as cmds

    # get the path where the file got autosaved
    mayaPath = os.getenv("TEMP")
    fullPath = os.path.join(mayaPath,"P4Maya_autosave")

    # remove the autosaved file
    files = os.listdir(fullPath)
    for file in files:
        filePath = os.path.join(fullPath,file)
        os.remove(filePath)
    
    # get current file
    currentFile = cmds.file(q=1,sn=1)
    
    # check if file is checked out
    status = GetStatus(currentFile)
    if status[0] == "Self":

        # save file
        cmds.file(s=1)

        # initialize perforce
        p4 = P4.P4()
        settings = GetSettings()
        if settings == None:
            cmds.warning("Settings are not set")
        else:
            p4.port = settings['port']
            p4.user = settings['user']
            p4.client = settings['client']

            # connect to server
            p4.connect()

            # shelf file
            depotfile = status[1][0]['depotFile']
            changelist = status[1][0]['change']
            p4.run_shelve('-f','-c',changelist,depotfile)

            # disconnect from server
            p4.disconnect()



### SET SETTINGS
def SetSettings(settingsDict):

    # get settings json directory
    import os
    mayaDir = os.getenv("MAYA_APP_DIR")
    settingsDir = os.path.join(mayaDir,"scripts/P4Maya/p4settings.json")
    
    # prepare settings dict
    import json
    settingsDict = [settingsDict]
    dataRaw = json.dumps(settingsDict,indent=4)

    # write to file
    with open(settingsDir,"w") as f:
        f.write(dataRaw)

    StartupScript()



### GET SETTINGS
def GetSettings():

    # get settings json directory
    import os
    mayaDir = os.getenv("MAYA_APP_DIR")
    settingsDir = os.path.join(mayaDir,"scripts/P4Maya/p4settings.json")

    # get settings
    import json
    with open(settingsDir,"r") as f:
        dataRaw = f.read()
    data = json.loads(dataRaw)

    # return settings as dict
    if len(data):
        return data[0]
    else:
        return None



### OPEN AUTO-SHELVED FILE
def OpenShelfed():
    import os
    import P4
    import maya.cmds as cmds
    import maya.mel as mel

    # get current file
    currentFile = cmds.file(q=1,sn=1)

    # initialize client and variables
    p4 = P4.P4()
    settings = GetSettings()
    if settings == None:
        cmds.warning("Settings are not set")
    else:
        p4.port = settings['port']
        p4.user = settings['user']
        p4.client = settings['client']

        # connect to the server
        p4.connect()
        
        # if file is checked out
        status = GetStatus(currentFile)
        if status[0] == "Self":
            
            # get the shelf file
            depotfile = status[1][0]['depotFile']
            changelist = status[1][0]['change']
            file = str(depotfile) + "@=" + str(changelist)
        
            # get the file info and contents
            try:
                filebytes = p4.run_print(file)
            
                # disconnect from server
                p4.disconnect()
                
                # get the temp location to save the shelved file at
                depotfile = filebytes[0]['depotFile']
                depotfile = depotfile.split('/')
                depotfile = depotfile[len(depotfile)-1]
                file, extension = os.path.splitext(depotfile)
                depotfile = str(file) + "@=" + str(changelist) + str(extension)
                temp = os.getenv("TEMP")
                file = os.path.join(temp,"p4v",depotfile)
                
                # get file contents
                contents = filebytes[1]
                
                # create a local file for the shelved file with the contents
                with open(file, 'wb') as f:
                    f.write(contents)
                    
                # get maya exe file
                mayaDir = mel.eval('getenv maya_location')
                maya = str(mayaDir+'/bin/maya.exe')
                mayaDirShortName = maya.replace("Program Files", "Progra~1")
                
                # boot up shelf file in new instance
                os.system("start " + mayaDirShortName + " " + file)
            
            # if there is no auto-shelved file yet
            except:
                cmds.warning("No files auto-shelved yet.")



### GET WORKSPACES
def GetWorkspaces(server,username):
    import P4
    import socket



    # initialize client and variables
    p4 = P4.P4()
    p4.port = server
    p4.user = username

    # connect to server
    p4.connect()

    # get user
    info = p4.run_info()
    user = info[0]['userName']

    # get workspaces
    workspaces = p4.run_clients('-u',user)
    localworkspaces = []
    for workspace in workspaces:
        if socket.gethostname() == workspace['Host']:
            localworkspaces.append(workspace['client'])

    # disconnect from server
    p4.disconnect()

    return localworkspaces



### OPEN SETTINGS MENU
def SettingMenu():
    import maya.cmds as cmds
    import json

    settings = GetSettings()
    portsetting = ""
    usersetting = ""
    if settings != None:
        portsetting = settings['port']
        usersetting = settings['user']

    # get workspaces
    def updateWorkspaces(a):
        serverText = cmds.textField(server,q=1,tx=1)
        userText = cmds.textField(user,q=1,tx=1)
        print(serverText,userText)
        workspaces = GetWorkspaces(serverText,userText)

        # loop through existing menus in the optionMenu and destroy them
        for item in cmds.optionMenu(workspace, q=True, ill=True) or []:
            cmds.deleteUI(item)
        
        for ws in workspaces:
            cmds.menuItem(label = ws, parent = workspace)



    # create submit window
    win = cmds.window("P4Maya Connection",
                    w=400,
                    h=175,
                    s=0)
    cmds.columnLayout(adjustableColumn=1)

    # top text
    cmds.text(f"Set up your Perforce connection",
            align="center",
            font="boldLabelFont",
            h=30)
    cmds.separator(h=10)

    # server input
    cmds.rowLayout(nc=2,w=400)
    cmds.text("Server",w=100,align="right")
    server = cmds.textField(tx=portsetting,width=290,h=30,tcc=updateWorkspaces)
    cmds.setParent("..")

    # user input
    cmds.rowLayout(nc=2,w=400)
    cmds.text("User",w=100,align="right")
    user = cmds.textField(tx=usersetting,width=290,h=30,tcc=updateWorkspaces)
    cmds.setParent("..")

    # submit type
    cmds.rowLayout(nc=2,w=400)
    cmds.text("Workspace",w=100,align="right")
    workspace = cmds.optionMenu(h=30,w=290)

    cmds.setParent("..")

    # submit command
    def applySettings(a):
        serverText = cmds.textField(server,q=1,tx=1)
        userText = cmds.textField(user,q=1,tx=1)
        workspaceText = cmds.optionMenu(workspace,q=1,v=1)
        settingsDict = {
                        "port": serverText,
                        "user": userText,
                        "client": workspaceText
                        }
        SetSettings(settingsDict)
        cmds.deleteUI(win)

    # buttons
    cmds.separator(h=10)
    cmds.rowLayout(nc=2,w=400)
    cmds.button("Apply",w=200,h=25,c=applySettings)
    cmds.button("Cancel",w=200,h=25,c="cmds.deleteUI('%s')" % win)

    # show window
    cmds.showWindow(win)