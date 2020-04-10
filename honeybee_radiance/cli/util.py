from ladybug.analysisperiod import AnalysisPeriod
from datetime import datetime
import copy


def get_hoys(start_date, start_time, end_date, end_time, timestep, leap_year):
    """Return list of hours from start date, star hour, end date and end hour.

    Date should be formatted as MMM-DD (e.g JUL-21) and hours must be formatted
    as HH:MM (e.g 18:30).
    """
    # convert datetimes
    try:
        start_date = datetime.strptime(start_date, '%b-%d')
    except ValueError as e:
        raise ValueError('Wrong input for start date:\n\t{}'.format(e))
    try:
        start_time = datetime.strptime(start_time, '%H:%M')
    except ValueError as e:
        raise ValueError('Wrong input for start time:\n\t{}'.format(e))
    try:
        end_date = datetime.strptime(end_date, '%b-%d')
    except ValueError as e:
        raise ValueError('Wrong input for end date:\n\t{}'.format(e))
    try:
        end_time = datetime.strptime(end_time, '%H:%M')
    except ValueError as e:
        raise ValueError('Wrong input for end time:\n\t{}'.format(e))

    org_end_time = copy.copy(end_time)
    if end_time.minute != 0:
        if end_time.hour != 23:
            end_time = datetime(
                end_time.year, end_time.month, end_time.day, end_time.hour + 1, 0
            )
        else:
            end_time = datetime(
                end_time.year, end_time.month, end_time.day + 1, 0, 0
            )
    ap = AnalysisPeriod(
        start_date.month, start_date.day, start_time.hour,
        end_date.month, end_date.day, end_time.hour,
        timestep, leap_year
    )

    hoys = ap.hoys

    # filter start and end hours if needed
    start_index = 0
    end_index = None
    if start_time.minute != 0:
        # remove the hours that are smaller than this hour
        for start_index, h in enumerate(hoys):
            if round(60 * h) % 60 >= start_time.minute:
                break

    if org_end_time.minute != 0:
        for end_index, h in enumerate(reversed(hoys)):
            if (60 * h) % 60 <= org_end_time.minute:
                break

    if start_index == 0 and end_index is None:
        return hoys
    elif end_index is None:
        return hoys[start_index:]
    else:
        return hoys[start_index: -1 * (end_index + 1)]
