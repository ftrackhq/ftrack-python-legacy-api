import ftrack
from uuid import uuid1 as uuid

def createProject():
    
    #create show
    showfullname = ftrack.getUUID()
    showname = ftrack.getUUID()
    workflows = ftrack.getProjectSchemes()
    w = None
    #make sure we get vfx workflow
    for workflow in workflows:
        if workflow.getId() == '69cb7f92-4dbf-11e1-9902-f23c91df25eb':
            w = workflow
    show = ftrack.createShow(showfullname,showname,w)
    
    return show

def createTasks(parent,total=1):
    tasks = []
    for i in range(0,total):
        IN_PROGRESS_STATUS = '44ddd0fe-4164-11df-9218-0019bb4983d8'
        DONE_STATUS = '44de097a-4164-11df-9218-0019bb4983d8'
        modeling = '44dc53c8-4164-11df-9218-0019bb4983d8'
        
        taskName1 = str(uuid())
        task = parent.createTask(taskName1,ftrack.TaskType(modeling),ftrack.TaskStatus(IN_PROGRESS_STATUS))
        tasks.append(task)
        
    if total == 1:
        return tasks[0]
        
    return tasks


    
        
        
        
        