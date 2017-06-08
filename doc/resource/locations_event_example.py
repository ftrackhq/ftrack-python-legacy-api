import ftrack
ftrack.setup()

from create_test_location import createTestLocation

sourceLocation = createTestLocation('test.location.a')
targetLocation = createTestLocation('test.location.b')


def transferComponentCallback(event, componentId=None, locationId=None):
    '''Copy a component from *sourceLocation* to *targetLocation*.'''
    if locationId == sourceLocation.getId():
        sourceComponent = sourceLocation.getComponent(componentId)

        # Add component to target location (and transfer any data)
        targetComponent = targetLocation.addComponent(sourceComponent)

        print(u'Transferred component {0} -> {1}'.format(
            sourceComponent.getInternalPath(),
            targetComponent.getInternalPath()
        ))

# Subscribe to the event
ftrack.EVENT_HUB.subscribe(
    ftrack.COMPONENT_ADDED_TO_LOCATION_TOPIC,
    transferComponentCallback
)

# Wait and process events (use Ctrl+C to abort)
ftrack.EVENT_HUB.wait()
