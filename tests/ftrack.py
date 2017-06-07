import os, sys

def _getLatestFile(path):
    filelist = os.listdir(path)
    filelist = filter(lambda x: not os.path.isdir(os.path.join(path,x)), filelist)
    newest = max(filelist, key=lambda x: os.stat(os.path.join(path,x)).st_mtime)
    return os.path.join(path,newest)



#build server
if os.path.isdir("/var/dev/ci/builds/FTClient"):
    egg = _getLatestFile("/var/dev/ci/builds/FTClient")
    os.environ["FTRACK_APIKEY"] = "7545384e-a653-11e1-a82c-f23c91df25eb"
    os.environ["FTRACK_SERVER"] = "https://skynet.ftrackapp.com"
    sys.path.append(egg)

    testDirectory = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.abspath(os.path.join(testDirectory, '..')))
    sys.path.append(testDirectory)

    os.environ['FTRACK_LOCATION_PLUGIN_PATH'] = os.path.join(
        testDirectory, 'plugin', 'location'
    )

#local
else:
    testDirectory = os.path.dirname(os.path.abspath(__file__))
    
    os.environ["FTRACK_SERVER"] = os.environ.get('FTRACK_SERVER',
                                                 'http://localhost:5005')
    
    sys.path.append(os.path.abspath(os.path.join(testDirectory, '..')))
    sys.path.append(testDirectory)

    os.environ['FTRACK_LOCATION_PLUGIN_PATH'] = os.path.join(
        testDirectory, 'plugin', 'location'
    )

from FTrackCore import *

