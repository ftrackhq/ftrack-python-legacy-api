..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/api_tutorial/using_time_reports:

******************
Using time reports
******************

The :term:`API` can be used to gather timelogs from all users to generate
various reports.

Read time reports for the last month for the current user::

    import getpass
    import datetime
    import calendar

    monthStart = datetime.date.today().replace(day=1)
    monthEnd = monthStart.replace(
        day=calendar.monthrange(monthStart.year, monthStart.month)[-1]
    )

    user = ftrack.User(getpass.getuser())

    # Get timelogs for user in current month.
    timelogs = user.getTimelogs(
        start=monthStart,
        end=monthEnd
    )

    # Sum total duration.
    totalDuration = 0
    for timelog in timelogs:
        totalDuration += timelog.get('duration')

    print '{0} logged {1} hours between {2:%x} and {3:%x}.'.format(
        user.getName(), totalDuration / 60 / 60, monthStart, monthEnd
    )
