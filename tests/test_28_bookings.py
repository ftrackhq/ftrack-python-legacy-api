from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys

from datetime import datetime, timedelta    

class test_Types:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass

    def test_1_create_booking(self):
        
        user = ftrack.getUsers()[0]

        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        booking = user.createBooking('description1', startdate, datetime.now() + timedelta(days=5), project=show)
        
        ok_(booking, 'User created correctly')
        
        ok_(booking.getUser().getId() == user.getId(), 'User is associated with booking')

        ok_(booking.getProject().getId() == show.getId(), 'Show is associated with booking')

    def test_2_metadata(self):

        from uuid import uuid1

        theid = str(uuid1())
        
        user = ftrack.getUsers()[0]

        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        booking = user.createBooking('description1', startdate, datetime.now() + timedelta(days=5), show)
        booking.setMeta('someid', theid)

        foundId = False
        for booking in show.getBookings():
            if booking.getMeta('someid') == theid:
                foundId = True
                break

        ok_(foundId, 'Created phase found and metadata set ok')

    @raises(ftrack.FTrackError)
    def test_3_delete(self):

        user = ftrack.getUsers()[0]

        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        booking = user.createBooking('description1', startdate, datetime.now() + timedelta(days=5), show)

        beforeDeleteShow = len(show.getBookings())
        beforeDeleteUser = len(user.getBookings())

        bookingId = booking.getId()

        booking.delete()

        ok_(len(show.getBookings()) == beforeDeleteShow-1, 'delete sucessful')
        ok_(len(user.getBookings()) == beforeDeleteUser-1, 'delete sucessful')

        # This should raise Exception
        ftrack.Booking(bookingId)

    @raises(ftrack.FTrackError)
    def test_4_date_is_none(self):
        user = ftrack.getUsers()[0]

        show = ftrack.getShow(['test'])        
        user.createBooking('description1', datetime.now(), None, show)

    def test_5_no_project(self):

        user = ftrack.getUsers()[0]

        bookingsBefore = len(user.getBookings())

        booking = user.createBooking('description1', datetime.now(), datetime.now() + timedelta(days=5))

        ok_(len(user.getBookings()) == bookingsBefore+1, 'create sucessful')



