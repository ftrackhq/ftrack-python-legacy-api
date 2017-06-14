# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
import tempfile
import urllib2
import filecmp
import ftestutil
from uuid import uuid1 as uuid

import ftrack
from ftrack import asc, desc, limit, order_by, filter_by

from .tools import ok_, raises, eq_


class test_Types:
    
    def __init__(self):
        '''Initialise test.'''
        self.globalName = 'nose_test'

    def test_1_publish_version(self):
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        
        asset = myShot.createAsset(name='my_first_asset',assetType='dai')
        comment = str(uuid())
        version = asset.createVersion(comment=comment,taskid=myTask.getId())
        
        ok_(asset.getType().get('short') == "dai", "Type is correct")
        
        #set attribute
        version.set('ilp_increment',999)
        
        quicktimeComponent = version.createComponent()
    
        #Export
        asset.publish()
        
        
        ok_(version.getComment() == comment, 'Written comment')
        #TODO - make sure this is a number
        ok_(version.get('ilp_increment') == 999, "Exported dailies")
        
        
        #Add thumbnail and verify by donwloading it from server
        thumbnailpath = os.path.join(
            os.path.dirname(__file__), 'data/thumbnail.jpg'
        )

        thumb = version.createThumbnail(thumbnailpath)
        version.setThumbnail(thumb)
        
        
        ok_(version.get('thumbid') == thumb.getId(),'Thumbnail was set')

        componentUrl = ftrack.Component(version.get('thumbid')).getUrl()

        _, temporaryPath = tempfile.mkstemp()
        try:
            u = urllib2.urlopen(componentUrl)
            localFile = open(temporaryPath, 'w')
            localFile.write(u.read())
            localFile.close()
            
            ok_(filecmp.cmp(temporaryPath, thumbnailpath),
                'Downloaded thumbnail and original thumbnail do not match.')
        
        finally:
            os.remove(temporaryPath)


    def test_2_versions_sort_order(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        
        asset = myShot.getAsset('custom',assetType='dai')
        
        versions = asset.getVersions()
        
        ok_(len(versions) == 35, "Number of versions")
        
        
        for i,v in enumerate(versions):
            
            if i == 0:
                continue
            
            ok_(v.getVersion() > versions[i-1].getVersion(), "Verify acending")
            
        
        
        
        
    def test_3_versions_advanced(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        
        asset = myShot.getAsset('custom',assetType='dai')
        
        versions = asset.getVersions(filter_by(username='bjorn.rydahl'),order_by(asc('ilp_version'),desc('ilp_increment')),limit(10))
        
        ok_(len(versions) == 10, "Number of versions is limited to 10")

        
        for i,v in enumerate(versions):
            
            ok_(v.getUser().getUsername() == 'bjorn.rydahl', "Verify user")
            
            if i == 0:
                continue

            
            ok_(v.get('ilp_version') >= versions[i-1].get('ilp_version'), "Verify asc " + str(v.get('ilp_version')) + " >= " + str(versions[i-1].get('ilp_version')))
            
        
            
        #filter by
        versions = asset.getVersions(filter_by(username='mattias.lagergren'))
        ok_(len(versions) == 5, "Number of versions filtered on mala is 5")
        
        
        
        
        #order by
        versions = asset.getVersions(order_by('ilp_increment'),limit(10))
        
        for i,v in enumerate(versions):
            
            if i == 0:
                continue

            ok_(v.get('ilp_increment') >= versions[i-1].get('ilp_increment'), "Verify ascending " + str(v.get('ilp_increment')) + " > " + str(versions[i-1].get('ilp_increment')))
            
    
        versions = asset.getVersions(filter_by(ilp_version='a'),order_by(asc('ilp_version'),desc('ilp_increment')),limit(10))
    

    
        for i,v in enumerate(versions):
            
            ok_(v.get('ilp_version') == 'a', "ilp_version is a")
            
            if i == 0:
                continue

            ok_(v.get('ilp_increment') < versions[i-1].get('ilp_increment'), "Verify desc " + str(v.get('ilp_increment')) + " < " + str(versions[i-1].get('ilp_increment')))
                
    
        ok_(len(versions) < 11, "Number of versions is < 11")



        versions = asset.getVersions(filter_by(version=35))
        ok_(len(versions) == 1, "Number of versions is 1")
    
    
        versions = asset.getVersions(filter_by("version > 30"))
        ok_(len(versions) == 5, "Number of versions is 5")
        
        
        versions = asset.getVersions(filter_by("version != 30"))
        ok_(len(versions) == 34, "Number of versions is 34")
        
        
    def test_4_versions_linked(self):

        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        
        asset = myShot.getAsset('custom',assetType='dai')
        
        versions = asset.getVersions(filter_by(username='bjorn.rydahl'),order_by(asc('ilp_version'),desc('ilp_increment')),limit(3))

        version1 = versions[0]
        version2 = versions[1]
        version3 = versions[2]
        
        
        #link versions
        version3.addUsesVersions(version1)
        version3.addUsesVersions([version2])

        
        #make sure it is linked in both directions
        usedInVersions = version1.usedInVersions()
        usesVersions = version3.usesVersions()
        
        
        ok_(len(usedInVersions) == 1, "Number of versions is 1")
        ok_(len(usesVersions) == 2, "Number of versions is 2")
        
        #correct versions?
        ok_(usedInVersions[0].getVersion() == version3.getVersion(), "Version is the same as before")
        ok_(usesVersions[0].getVersion() == version1.getVersion() or usesVersions[0].getVersion() == version2.getVersion(), "Version is the same as before")
        
        
        #unlink version
        version3.removeUsesVersions(version1)
        usesVersions = version3.usesVersions()
        
        ok_(len(usesVersions) == 1, "Number of versions is 1")
        ok_(usesVersions[0].getVersion() == version2.getVersion(), "Version is version2")
        
        version3.addUsesVersions([version1.getId()])
        ok_(len(usesVersions) == 1, "Number of versions is 2")
        
        version3.removeUsesVersions([version1.getId()])
        ok_(len(usesVersions) == 1, "Number of versions is 1")


#    def test_6_reserve_version_number(self):
#        myShot = ftrack.getShotFromPath("test.python_api.shot1")
#        myTask = myShot.getTasks()[0]
#        
#        asset1 = myShot.createAsset(name='my_first_asset',assetType='dai')
#        version1 = asset1.createVersion(taskid=myTask.getId())
#        take1 = version1.createComponent(path="nofile")
#    
#        asset2 = myShot.createAsset(name='my_first_asset',assetType='dai')
#        version2 = asset2.createVersion(taskid=myTask.getId())
#        take2 = version2.createComponent(path="nofile")    
#    
#        #Export
#        asset2.publish()
#        asset1.publish()
#        
#        print version1.get('version')
#        print version2.get('version')
#        ok_(version1.get('version') < version2.get('version'), "Version1 is smaller than version2")  
#        
#        
        
        
    def test_7_publish_version_using_getAsset(self):
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        
        asset = myShot.getAsset(name='my_first_asset',assetType='dai')
        version = asset.createVersion(taskid=myTask.getId())
        
        ok_(asset.getType().get('short') == "dai", "Type is correct")
        
        #set attribute
        version.set('ilp_increment',999)
        
        quicktimeComponent = version.createComponent()

        #Export
        asset.publish()
        
        #TODO - make sure this is a number
        ok_(version.get('ilp_increment') == 999, "Exported dailies")
        
        
    def test_8_publish_version_addmeta(self):
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        
        asset = myShot.createAsset(name='my_first_asset',assetType='dai')
        version = asset.createVersion(taskid=myTask.getId())
        
        quicktimeComponent = version.createComponent()
        quicktimeComponent2 = version.createComponent(name='proxy')
    
        #Export
        asset.publish()
        
        #set meta
        version.setMeta('metatest','test1')   
        quicktimeComponent.setMeta('metatest','test2')
        quicktimeComponent.setMeta('metatest2',6) 
        
        ok_(version.getMeta('metatest') == 'test1', "Set meta on version")
        ok_(quicktimeComponent.getMeta('metatest') == 'test2', "Set meta on take")
        ok_(quicktimeComponent.getMeta('metatest2') == '6', "Set meta on take")
        
        ok_(quicktimeComponent.getMeta('metatest3') == None, "Set meta on take")
        
        
    def test_9_version_with_no_taskid(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        
        asset = myShot.createAsset(name='my_first_asset',assetType='dai')
        version = asset.createVersion(taskid=None)

        quicktimeComponent = version.createComponent()

        #Export
        asset.publish()
                
        thumbnailpath = os.path.join(
            os.path.dirname(__file__), 'data/thumbnail.jpg'
        )

        thumb = version.createThumbnail(thumbnailpath)
        
    def test_11_asset_with_taskid(self):
        """
        Test to associate task directly with asset
        """
        
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai',task=myTask)
        version = asset.createVersion(taskid=myTask.getId())

        quicktimeComponent = version.createComponent()
    
        #Export
        asset.publish()
        
        assets = myTask.getAssets()
        
        found = False
        for asset in assets:
            if asset.getName() == assetName:
                found = True
                
        ok_(found,'asset was found through versions taskid')
        

        
        
        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai',task=myTask)
        version = asset.createVersion()

        quicktimeComponent = version.createComponent()
    
        #Export
        asset.publish()
        
        assets = myTask.getAssets()
        
        found = False
        for asset in assets:
            if asset.getName() == assetName:
                found = True
                
        ok_(found,'asset was found through asset only')
        
        
        
        ok_(version.getTask().getId() == myTask.getId(),'version can find its task')
        
        versions = myTask.getAssetVersions()
        ok_(len(versions) > 0,'versions can be found')
        
        ok_(isinstance(versions[0],ftrack.AssetVersion),'Is type assetversion')
            
            
            
    def test_12_publish_on_seqeunce(self):
       import sys
       
       myProject = ftrack.getProject("test")
       mySequence = ftrack.getSequenceFromPath("test.python_api")
       #myTask = mySequence.getTasks()[0]
       
       asset = mySequence.createAsset(name='my_first_asset',assetType='dai')
       version = asset.createVersion(taskid=None)

       assetFolder = myProject.getPath(True)
       quicktimeComponent = version.createComponent()

       #Export
       asset.publish()
       
       assets = mySequence.getAssets()
       
       found = False
       for a in assets:
           if a.getId() == asset.getId():
               found = True
               
       ok_(found,'Assets can be queried')
        
        
    def test_13_get_assets_component_name(self):

        
        mySequence = ftrack.getShotFromPath("test.python_api")
        myShot = mySequence.createShot(str(uuid()))
        myTask = myShot.createTask('taskname',ftrack.TaskType("Modeling"),ftrack.TaskStatus('In Progress'))

        assetName1 = str(uuid())
        asset = myShot.createAsset(name=assetName1,assetType='dai',task = myTask)
        version = asset.createVersion()

        
        test1 = version.createComponent(name='test1')
        test2 = version.createComponent(name='test2')

        version.publish()

        version = asset.createVersion()

        test1 = version.createComponent(name='test1')
        test2 = version.createComponent(name='test4')

        version.publish()

        assetName2 = str(uuid())
        asset2 = myShot.createAsset(name=assetName2,assetType='dai',task = myTask)
        version = asset2.createVersion()

        
        test1 = version.createComponent(name='test33')
        test2 = version.createComponent(name='test2')

        version.publish()

        version = asset2.createVersion()

        test1 = version.createComponent(name='test33')
        test2 = version.createComponent(name='test2')

        version.publish()

        eq_(len(myShot.getAssets()), 2, "should be two assets")


        eq_(len(myShot.getAssets(componentNames=['test2'])), 2, "should be two assets")

        eq_(len(myShot.getAssets(componentNames=['test33'])), 1, "should be one assets")

        eq_(len(myShot.getAssets(componentNames=['test335'])), 0, "should be zero assets")



        eq_(len(myTask.getAssets()), 2, "should be two assets")


        eq_(len(myTask.getAssets(componentNames=['test2'])), 2, "should be two assets")

        eq_(len(myTask.getAssets(componentNames=['test33'])), 1, "should be one assets")

        eq_(len(myTask.getAssets(componentNames=['test335'])), 0, "should be zero assets")




        #get versions
        eq_(len(asset.getVersions(componentNames=['test2'])), 1, "should be one v")

        eq_(len(asset.getVersions(componentNames=['test1'])), 2, "should be two v")

        eq_(len(asset.getVersions(componentNames=['test335'])), 0, "should be zero v")


        eq_(len(asset2.getVersions(componentNames=['test2'])), 2, "should be two v")

        eq_(len(asset2.getVersions(componentNames=['test33'])), 2, "should be two v")

        eq_(len(asset2.getVersions(componentNames=['test335'])), 0, "should be zero v")


        #clean
        myShot.delete()

    def test_14_publish(self):

        #make sure we can publish a version later
        myShot = ftrack.getShotFromPath("test.python_api.shot1")

        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai')
        version1 = asset.createVersion()
        version2 = asset.createVersion()
        
        quicktimeComponent = version2.createComponent()

        version = ftrack.AssetVersion(version2.getId())
        ok_(version.get('ispublished') == False, 'is not published')

        newAsset = ftrack.Asset(asset.getId())
        newAsset.publish()

        version = ftrack.AssetVersion(version2.getId())
        ok_(version.get('ispublished') == True, 'is published')

        version1 = ftrack.AssetVersion(version1.getId())
        version2 = ftrack.AssetVersion(version2.getId())

        ok_(version1.get('ispublished') == False, 'is not published')
        ok_(version2.get('ispublished') == True, 'is published')


        #make sure we can publish a version later without components
        myShot = ftrack.getShotFromPath("test.python_api.shot1")

        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai')
        version1 = asset.createVersion()
        version2 = asset.createVersion()

        version = ftrack.AssetVersion(version2.getId())
        ok_(version.get('ispublished') == False, 'is not published')

        newAsset = ftrack.Asset(asset.getId())
        newAsset.publish()

        version = ftrack.AssetVersion(version2.getId())
        ok_(version.get('ispublished') == True, 'is published')

        version1 = ftrack.AssetVersion(version1.getId())
        version2 = ftrack.AssetVersion(version2.getId())

        ok_(version1.get('ispublished') == False, 'is not published')
        ok_(version2.get('ispublished') == True, 'is published')




        #publish on the version
        myShot = ftrack.getShotFromPath("test.python_api.shot1")

        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai')
        version1 = asset.createVersion()
        version2 = asset.createVersion()

        version = ftrack.AssetVersion(version2.getId())
        ok_(version.get('ispublished') == False, 'is not published')

        newAsset = ftrack.Asset(asset.getId())
        version.publish()

        version = ftrack.AssetVersion(version2.getId())
        ok_(version.get('ispublished') == True, 'is published')

        version1 = ftrack.AssetVersion(version1.getId())
        version2 = ftrack.AssetVersion(version2.getId())

        ok_(version1.get('ispublished') == False, 'is not published')
        ok_(version2.get('ispublished') == True, 'is published')
        

    def test_15_getasset_with_assettypesfilter(self):

        seq = ftrack.getShotFromPath("test.python_api")
        shot = seq.createShot(ftrack.getUUID())

        asset = shot.createAsset(name="a1",assetType='dai')
        asset = shot.createAsset(name="a2",assetType='geo')

        assets = shot.getAssets(assetTypes=['dai'])
        print len(assets)
        ok_(len(assets) == 1, 'shoudl be one')

        assets = shot.getAssets()
        print len(assets)
        ok_(len(assets) == 2, 'shoudl be one')

    @raises(ftrack.FTrackError)
    def test_16_publish_on_task(self):

        seq = ftrack.getShotFromPath("test.python_api")
        shot = seq.createShot(ftrack.getUUID())
        task = shot.createTask('taskname',ftrack.TaskType("Modeling"),ftrack.TaskStatus('In Progress'))
        asset = task.createAsset(name="a1",assetType='dai')

    def test_getassets_without_tasks(self):

        p = ftestutil.createProject()
        shot = p.createShot('010')
        myTask = ftestutil.createTasks(shot)

        asset1 = shot.createAsset(name='a1',assetType='dai')
        version = asset1.createVersion(taskid=myTask.getId())
        take = version.createTake()

        version.publish()

        asset2 = shot.createAsset(name='a2',assetType='dai')
        version = asset2.createVersion()
        take = version.createTake()

        version.publish()

        asset3 = shot.createAsset(name='a3',assetType='dai')

        assets = shot.getAssets()

        ok_(len(assets) == 3, 'there should be three assets')

        assets = shot.getAssets(excludeWithTasks=True)

        ok_(len(assets) == 1, 'there should be one assets')

        ok_(assets[0].getName() == 'a2', 'Expected a2')


        #make sure we can still filter on component names at the same time
        assets = shot.getAssets(excludeWithTasks=True,componentNames=['main'])

        #remove project
        p.delete()

    def testPublishOnProject(self):
        '''Publish a version on the project.'''
        project = ftestutil.createProject()
        asset = project.createAsset(name='assetname', assetType='dai')
        version = asset.createVersion()
        version.publish()

        assets = project.getAssets()
        eq_(len(assets), 1, 'One asset exists.')
        versions = assets[0].getVersions()
        eq_(len(versions), 1, 'One version exists.')
