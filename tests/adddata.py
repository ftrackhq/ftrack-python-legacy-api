import ftrack,sys
from random import randint
#create show
showfullname = 'test6'
showname = 'test6'
workflows = ftrack.getProjectSchemes()
show = ftrack.createShow(showfullname,showname,workflows[0])

taskTypes = show.getTaskTypes()
taskStatuses = show.getTaskStatuses()

for k in range(1,100):
    #create sequence
    seqname = ftrack.getUUID()
    seq = show.createSequence(seqname)
    
    

    for i in range(1,100):
        #create shot
        shotname = ftrack.getUUID()
        shot = seq.createShot(shotname)

        for j in range(1,20):
            
            sys.stdout.write(".")
            #create tasks
            taskType = taskTypes[randint(0,len(taskTypes)-1)]
            taskStatus = taskStatuses[randint(0,len(taskStatuses)-1)]
            
            
            taskname = ftrack.getUUID()
            task = shot.createTask(taskname,taskType,taskStatus)