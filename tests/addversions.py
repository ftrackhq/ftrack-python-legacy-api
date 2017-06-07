import ftrack,sys


myShot = ftrack.getShotFromPath("test.python_api.shot1")
myTask = myShot.getTasks()[0]


import time
start = time.time()

for i in range(0,1):

    asset = myShot.createAsset(name='my_first_asset',assetType='dai')
    version = asset.createVersion(taskid=myTask.getId())
    
    quicktimeComponent = version.createComponent()

    #Export
    asset.publish()

end = time.time()

print (end-start)