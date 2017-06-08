import time
import tempfile

import ftrack
ftrack.setup()

from create_test_location import createTestLocation

sourceLocation = createTestLocation('test.location.a')
targetLocation = createTestLocation('test.location.b')

(_, componentPath) = tempfile.mkstemp(suffix='.txt')
component = ftrack.createComponent(path=componentPath, location=sourceLocation)

# Sleep for ten seconds to allow the component to be transferred.
time.sleep(10)

componentId = component.getId()
availability = targetLocation.getComponentAvailability(componentId)

if availability > 0.0:
    print 'Success! Component is available in target location.'
else:
    print 'Component is NOT available in target location.'
