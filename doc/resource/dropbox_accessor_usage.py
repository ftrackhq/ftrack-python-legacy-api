import tempfile
import ftrack
from dropbox_accessor import DropboxAccessor

access_token = u'YOUR ACCESS TOKEN'
accessor = DropboxAccessor(access_token)

# Create a test location
location = ftrack.ensureLocation('test.dropbox')
location = ftrack.Location(
    'test.dropbox',
    accessor=accessor,
    structure=ftrack.IdStructure(),
    priority=10
)

# Create a test component with some content
(_, componentPath) = tempfile.mkstemp(suffix='.txt')
fileHandler = open(componentPath, 'wb')
fileHandler.write('Hello world!')
fileHandler.close()
component = ftrack.createComponent(path=componentPath, location=location, manageData=True)

# Check component availabilty and retreive the contents
availabilty = location.getComponentAvailability(component.getId())
print 'Component availabilty:', availabilty

resource = component.getResourceIdentifier()
contents = accessor.open(resource).read()
print 'Component data:'
print contents
