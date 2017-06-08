import ftrack


def myCallback(event):
    '''Dynamic enumerator service callback.

    event['data'] is expected to contain:

        * attributeName - The name of the custom attribute.
        * recordData - Information about changes to the entity.

    '''
    changes = event['data']['recordData'].get('changes', {})
    attributeName = event['data']['attributeName']

    output = []
    if attributeName == 'product_category':
        # Handle product_category.
        output = [
            {
                'name': 'Furniture',
                'value': 'furniture'
            }, {
                'name': 'Car',
                'value': 'car'
            }
        ]

    elif attributeName == 'product_name':
        # Handle product_name based on product_category. This will only work
        # if product_category is passed with changes, which will happen when
        # creating projects for example. product_category could also be
        # queried using the API.

        selectedProductCategory = changes.get('product_category')

        if selectedProductCategory == 'furniture':
            output = [{
                'name': 'Chair',
                'value': 'chair'
            }, {
                'name': 'Table',
                'value': 'table'
            }]

        elif selectedProductCategory == 'car':
            output = [{
                'name': 'Saab',
                'value': 'saab'
            }, {
                'name': 'Volvo',
                'value': 'volvo'
            }]

    else:
        # Output some test data.
        output = [{
            'name': 'Test A',
            'value': 'test_a'
        }, {
            'name': 'Test B',
            'value': 'test_b'
        }]

    return output


# Subscribe to the dynamic enumerator topic.
ftrack.setup()
ftrack.EVENT_HUB.subscribe('topic=ftrack.dynamic-enumerator', myCallback)
ftrack.EVENT_HUB.wait()
