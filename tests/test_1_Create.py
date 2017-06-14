# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack
import os
from uuid import uuid1 as uuid

import ftrack

from .tools import ok_


class test_Types:
    
    def __init__(self):
        '''Initialise test.'''
        self.globalName = 'nose_test'

    def test_1_create(self):
        
        #create show
        showfullname = ftrack.getUUID()
        showname = ftrack.getUUID()
        workflows = ftrack.getProjectSchemes()
        show = ftrack.createShow(showfullname,showname,ftrack.ProjectScheme('VFX Scheme'))
        
        
        #create sequence
        seqname = ftrack.getUUID()
        seq = show.createSequence(seqname)
        
        
        #create shot
        shotname = ftrack.getUUID()
        shot = seq.createShot(shotname)
        
        shot.getSequence()
        
        asset = shot.createAsset(name='test',assetType='dai')
        version = asset.createVersion()
        
        quicktimeComponent = version.createComponent()

        #Export
        asset.publish()        
        
        #create tasks
        taskType = show.getTaskTypes()[0]
        taskStatus = show.getTaskStatuses()[0]
        task = None
        for i in range(1,6):
            taskname = ftrack.getUUID()
            task = shot.createTask(taskname,taskType,taskStatus)
        
        ok_(len(shot.getTasks()) == 5,'created 5 tasks')

    def test_2_notes_and_attachments(self):
        myShow = ftrack.getShowFromPath("test")
        mySeq = ftrack.getSequenceFromPath("test.python_api")
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        myVersion = myShot.getAssets()[0].getVersions()[-1]
        
        def testNotes(entity):
            noteText = str(uuid())
            note = entity.createNote(noteText)

            path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), 'data/attachment.txt')
            )

            attachment = note.createAttachment(path)

            ok_(note.getText() == noteText, "Note is the same")
            
            notes = entity.getNotes()

            ok_(notes[-1].getText() == noteText, "Last Note is the same")

        testNotes(myShow)
        testNotes(mySeq)
        testNotes(myShot)
        testNotes(myTask)
        testNotes(myVersion)
        

        #add note with category
        categories = ftrack.getNoteCategories()
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        
        note1 = myShot.createNote('note',categories[0])
        note2 = myShot.createNote('note',categories[1])
        

        ok_(note1.getCategory().getId() == categories[0].getId(), "Category1 was set")
        ok_(note2.getCategory().getId() == categories[1].getId(), "Category2 was set")

        ok_(categories[0].getId() != categories[1].getId(), "Categories are different")

    def test_3_notes_on_notes(self):
        myShow = ftrack.getShowFromPath("test")
        mySeq = ftrack.getSequenceFromPath("test.python_api")
        myShot = ftrack.getShotFromPath("test.python_api.shot2")
        
        count = len(myShot.getNotes())
        
        id1 = str(uuid())
        id2 = str(uuid())
        
        note = myShot.createNote(id1)
        reply = note.createReply(id2)
        
        notes = note.getNotes()
        
        ok_(len(notes) == 1, "one reply found")
        
        ok_(notes[0].getText() == id2,'Text in reply is found')
        
        ok_(len(myShot.getNotes()) == 2 + count, "Two more notes than from the start")
        
        ok_(note.isReply() == False, "Is not reply")
        ok_(reply.isReply() == True, "Is reply")
        
        
        
        