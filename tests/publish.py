
import os

os.environ["FTRACK_SERVER"] = "http://localhost:5005"
os.environ["LOGNAME"] = 'habe'

import ftrack,sys

from random import randint








def addVersion(shot,thumb,name,_type,user,comment=""):
    
    os.environ["LOGNAME"] = user
    
    myShot = ftrack.getShotFromPath(shot)
    myTask = myShot.getTasks()[randint(0,len(myShot.getTasks())-1)]
    
    
    asset = myShot.createAsset(name=name,assetType=_type)
    version = asset.createVersion(comment=comment,taskid=myTask.getId())
    
    
    quicktimeComponent = version.createComponent()
    
    #Export
    asset.publish()

    thumbnailpath = os.path.join(
        os.path.dirname(__file__), 'data', thumb
    )
    

    thumb = version.createThumbnail(thumbnailpath)
    
    
addVersion(['dvs','assets','a1-vraptor'],'veloBlood.jpg','vraptor','geo','anny',"Did changes based on client feedback")

addVersion(['dvs','assets','a2-desert'],'desert2.jpg','vraptor','geo','peav',"Work in progress")

addVersion(['dvs','assets','a3-trex'],'trex.jpg','trex','render','anny',"Fixed flicker at the end of the sequence")

addVersion(['dvs','assets','a4-forest'],'forest.jpg','forest','render','peav','Did changes based on client feedback')

addVersion(['dvs','assets','a6-diplodocus'],'diplodocus.jpg','dipodocus','render','casc','Work in progress')




addVersion(['dvs','cav010','010'],'trico.jpg','trico','render','anny','Fixed flicker at the end of the sequence')
addVersion(['dvs','cav010','010'],'trico.jpg','trico','render','anny','Did changes based on client feedback')

addVersion(['dvs','des010','010'],'desert2.jpg','desert','render','stli','Published for client feedback')
addVersion(['dvs','des010','010'],'desert2.jpg','desert','render','stli','Did changes based on client feedback')

addVersion(['dvs','for010','010'],'forest.jpg','forest','render','stli','Work in progress')
addVersion(['dvs','for010','010'],'forest.jpg','forest','render','stli','Published for client feedback')





