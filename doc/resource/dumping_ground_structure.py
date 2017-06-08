# :coding: utf-8

import ftrack


class DumpingGroundStructure(ftrack.Structure):
    '''Dumping ground structure.

    Follows pattern:

        /{prefix}/{parentHierarchy}_{assetType}_{version}_{componentName}.{componentFileType}

    For example:

        /data/myjob_001_010_model_geo_v001_main.ma

    .. warning::

        Not recommended for production use.

    '''

    def getResourceIdentifier(self, entity):
        '''Return a :term:`resource identifier` for supplied *entity*.

        .. note::

            Only supports :py:class:`~ftrack.Component` entities.

        '''
        if not isinstance(entity, ftrack.Component):
            raise NotImplementedError('Cannot generate resource identifier for '
                                      'unsupported entity {0}'.format(entity))

        component = entity

        # Can't generate identifier for a non-sequence container component.
        if (
            component.isContainer()
            and component.getSystemType() != 'sequence'
        ):
            raise NotImplementedError('Cannot generate resource identifier for '
                                      'container component {0}'.format(entity))

        container = component.getContainer()
        if container:
            # Use container for consistency across sibling members.
            hierarchy = container.getParents()
        else:
            hierarchy = component.getParents()

        # Construct structure.
        structure = []

        if self.prefix:
            structure.append(self.prefix)

        # Compute and add new filename if appropriate. Note that a sequence will
        # have a file name in the form prefix.%04d.ext.
        # E.g. test_sc010_010_spacestationLights_img_v001_main.%04d.exr
        fileNameStructure = self._getHierarchyStructure(hierarchy)

        if container:
            # Use container name for consistency across sibling members.
            fileNameStructure.append(container.getName())
        else:
            fileNameStructure.append(component.getName())

        fileName = '_'.join(fileNameStructure)

        if container:
            # Member of a container so add entity name as index.
            fileName += '.{0}'.format(entity.getName())

        elif component.getSystemType() in ('sequence',):
            # Add a sequence identifier.
            sequenceExpression = self._getSequenceExpression(component)
            fileName += '.{0}'.format(sequenceExpression)

        if fileName is not None:
            if container:
                # Use container extension for consistency across sibling
                fileType = container.getFileType()
            else:
                fileType = component.getFileType()

            if fileType:
                fileName += component.getFileType()

            structure.append(fileName)

        return self.pathSeparator.join(structure)

    def _getHierarchyStructure(self, hierarchy):
        '''Return structure for *hierarchy*.

        Examine the *hierarchy* and return ordered list of names to use for
        structure.

        Example result::

            ['myproject', 'sc001', '010', 'render', 'img', 'v001']

        '''
        structure = []

        for ancestor in reversed(hierarchy):
            try:
                name = ancestor.getName()

            except AttributeError:
                if isinstance(ancestor, ftrack.AssetVersion):
                    # Add padded version number for asset version.
                    version = 'v{0:03d}'.format(ancestor.getVersion())
                    structure.append(version)

                continue

            if isinstance(ancestor, ftrack.Component):
                # Ignore intermediate components.
                continue

            else:
                name = name.lower().replace(' ', '_')
                structure.append(name)

                if isinstance(ancestor, ftrack.Asset):
                    # Add asset type short code.
                    assetType = ancestor.getType().getShort()
                    structure.append(assetType)

        return structure
