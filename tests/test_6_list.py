from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys

class test_Types:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass


       
    def test_1_create_list(self):
        
        show = ftrack.getShow(['test'])
        categories = ftrack.getListCategories()
        
        ok_(len(categories) > 0,"There are list categories")
        
        myList = show.createList(ftrack.getUUID(),categories[0],ftrack.Shot)
        myList2 = show.createList(ftrack.getUUID(),categories[0],ftrack.Task)
        myList3 = show.createList(ftrack.getUUID(),categories[0],ftrack.AssetVersion)
        
        ok_(len(myList) == 0,"The list is empty")
        
        
        shot1 = ftrack.getShot(['test','python_api','shot1'])
        shot2 = ftrack.getShot(['test','python_api','shot2'])     
        
        myList.append(shot1)

        ok_(len(myList) == 1,"The list has one item")


        lists = show.getLists()
        
        ok_(len(lists) > 0,"The are lists on this show")
        
        myList.remove(shot1)
        
        ok_(len(myList) == 0,"The list is empty")
        
        
        myList.extend([shot1,shot2])
        
        ok_(len(myList) == 2,"The list has two items")
        
        #[] operator
        ok_(myList[0],"get item")
        
        myList.remove([shot1,shot2])
        
        ok_(len(myList) == 0,"The list is empty")
        
        
        
        ok_(myList.isOpen(),"The list is open")
        
        myList.close()
        
        ok_(myList.isOpen() == False,"The list is closed")
        
        
        myList.open()
        
        ok_(myList.isOpen(),"The list is open")
        
        

        
        v = shot1.getAssets()[0].getVersions()[0]

        myList3.append(v)
        
        ok_(len(myList3) == 1,"The list is not empty")

        myList3.remove(v)
        ok_(len(myList3) == 0,"The list is empty")
        
        
    def test_2_link_task_to_list(self):
        categories = ftrack.getListCategories()
        show = ftrack.getShow(['test'])
        shot1 = ftrack.getShot(['test','python_api','shot2'])
        task1 = shot1.getTasks()[0]
        task2 = shot1.getTasks()[1]
        
        myList = show.createList(ftrack.getUUID(),categories[0],ftrack.Task)
        
        
        myList.link(task1)
        
        
        linked = myList.getLinked()
        
        ok_(len(linked) == 1,"Linked items are 1")
        
        ok_(linked[0].getId() == task1.getId(),"Task id is correct")
        
        
        foundLists = task1.getLists()
        found = False
        for _list in foundLists:
            if _list.getId() == myList.getId():
                found = True
        
        ok_(found,"List id is correct")
        
        
        myList.unlink(task1)
        
        linked = myList.getLinked()
        
        ok_(len(linked) == 0,"Linked items are 0")
        
        
        myList.link(task1)
        myList.link(task2)
        
        linked = myList.getLinked()
        
        ok_(len(linked) == 2,"Linked items are 2")
        
        
    def test_3_attribute_on_list(self):
        
        categories = ftrack.getListCategories()
        show = ftrack.getShow(['test'])
        shot1 = ftrack.getShot(['test','python_api','shot2'])
        task1 = shot1.getTasks()[0]
        task2 = shot1.getTasks()[1]
        
        myList = show.createList(ftrack.getUUID(),categories[0],ftrack.Task)
        
        newName = ftrack.getUUID()
        
        myList.set('name',newName)
        
        
        ok_(myList.get('name') == newName,"Linked items are 2")
        
        myList.set('listbool',True)
        
        ok_(myList.get('listbool') == True,"is true")
        
        myList.set('listbool',False)
        
        ok_(myList.get('listbool') == False,"is false")
        
    def test_4_list_by_name(self):
        
        categories = ftrack.getListCategories()
        show = ftrack.getShow(['test'])
        shot1 = ftrack.getShot(['test','python_api','shot2'])
        task1 = shot1.getTasks()[0]
        task2 = shot1.getTasks()[1]
        listName = ftrack.getUUID()
        myList = show.createList(listName,categories[0],ftrack.Task)
        
        myList2 = show.getList(listName)
        
        
        ok_(myList2.getId() == myList.getId(),"same list")

    def test_5_list_iterator(self):
        
        categories = ftrack.getListCategories()
        show = ftrack.getShow(['test'])
        shot1 = ftrack.getShot(['test','python_api','shot1'])
        shot2 = ftrack.getShot(['test','python_api','shot2'])

        myList = show.createList(ftrack.getUUID(),categories[0],ftrack.Task)
        
        
        myList.extend([shot1,shot2])
        
        ok_(len(myList) == 2,"The list has two items")
        
        
        found = 0
        
        for item in myList:
            if item.getId() == shot1.getId():
                found += 1
        
            if item.getId() == shot2.getId():
                found += 1
                
        ok_(found == 2,"The list has two items")
        

    @raises(ftrack.FTrackError)
    def test_6_list_duplicate(self):
        
        categories = ftrack.getListCategories()
        show = ftrack.getShow(['test'])
        
        listname = ftrack.getUUID()
        myList = show.createList(listname,categories[0],ftrack.Task)
        myList = show.createList(listname,categories[0],ftrack.Task)        
          
    def test_7_getlists_filter(self):

        
        def findList(lists,name):

            for l in lists:
                if l.getName() == name:
                    return True

            return False


        categories = ftrack.getListCategories()
        show = ftrack.getShow(['test'])
        
        listname = ftrack.getUUID()
        myList = show.createList(listname,categories[1],ftrack.Task)


        lists = show.getLists()

        ok_(findList(lists,listname), 'list was found without filter')



        lists = show.getLists(categories=[categories[1]])

        ok_(findList(lists,listname), 'list was found with filter')


        lists = show.getLists(categories=[categories[0]])

        ok_(findList(lists,listname) == False, 'list was not found with filter')




        lists = show.getLists(name=listname[4:12],categories=[categories[1]])

        ok_(findList(lists,listname), 'list was found with filter')



        lists = show.getLists(name=listname[4:12])

        ok_(findList(lists,listname), 'list was found with filter')


        lists = show.getLists(name="hejhej")

        ok_(findList(lists,listname) == False, 'list was not found with filter')


    def test_8_add_values_to_listobject(self):
        import ftestutil
        
        categories = ftrack.getListCategories()
#        
        project = ftrack.getProject("test")
#        
        myList = project.createList(ftrack.getUUID(),categories[0],ftrack.Shot)
#        
#        shot1 = ftrack.getShot(['test','python_api','shot2'])
#        print shot1
#        print myList
        
        shot1 = ftrack.Task("b519f882-b61c-11e1-8be1-f23c91df25eb")
        #myList = ftrack.List("55752940-7775-11e2-95b1-0019bb4983d8")
        
        
        
        myList.append(shot1)
        
        
        val = myList.getValue(shot1,'mytest')
        
        ok_(val == False,'value must be set')
        
        
        val = myList.setValue(shot1,'mytest',True)
        
        
        val = myList.getValue(shot1,'mytest')
        
        ok_(val == True,'value must be set')
        
        
        
        val = myList.setValue(shot1,'mytest',False)