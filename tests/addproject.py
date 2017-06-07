import os

os.environ["FTRACK_SERVER"] = "http://cinesite.ftrack.com"

import ftrack,sys

#create show
showfullname = "demo"
showname = "demo"
workflows = ftrack.getProjectSchemes()
show = ftrack.createShow(showfullname,showname,workflows[0])