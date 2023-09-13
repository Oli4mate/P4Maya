### P4Maya for Maya2023
### by Olivier Dral
###
### Beta version 0.1
### 1-7-2023
### 
### For any issues, please reach out to me at oli4dral@gmail.com.


# P4MAYA STARTUP SCRIPT


maya.utils.executeDeferred('''

def run():
    import P4Maya.P4Commands as P4Maya

    P4Maya.StartupScript()

run()
cmds.scriptJob(event=["SceneOpened", run])

''')