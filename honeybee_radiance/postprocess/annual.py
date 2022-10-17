"""Shared functions for post-processing annual results."""
import json
import os

from ..writer import _filter_by_pattern


def generate_default_schedule(weekday=None, weekend=None):
    """Create a list of 8760 values based on a daily schedule for weekend and weekday.

    Args:
        weekday: A list of 24 values for each hour of a weekday. The values can
            be 0 or 1.
        weekend: A list of 24 values for each hour of a weekend day. The values can
            be 0 or 1.

    Returns:
        List -- A list of 8760 values for the year.

    """
    weekend = weekend or [0] * 24
    weekday = weekday or \
        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    assert len(weekend) == 24, 'Weekend list should be 24 values.'
    assert len(weekday) == 24, 'Weekend list should be 24 values.'
    weekend = [0 if v == 0 else 1 for v in weekend]
    weekday = [0 if v == 0 else 1 for v in weekday]
    all_values = []
    day_counter = 0
    week_counter = 1
    while day_counter < 365:
        day_counter += 1
        if week_counter < 7:
            if week_counter == 1:
                all_values.extend(weekend)
            else:
                all_values.extend(weekday)
            week_counter += 1
        else:
            all_values.extend(weekend)
            week_counter = 1
    return all_values


# TODO: support smaller timesteps - currently this works only for hourly calculations
def filter_schedule_by_hours(sun_up_hours, schedule=None):
    """Filter an annual schedule based on sun up hours.

    Args:
        sun_up_hours: A list of sun up hours as integers.
        schedule: A list of 8760 values for the occupancy schedule.

    Returns:
        A tuple with two values.

        occ_pattern -- A filtered version of the annual schedule that only
            includes the sun-up-hours.

        total_hours -- An integer for the total occupied hours of the schedule.

        sun_down_occ_hours -- An integer for the number of occupied hours where
            the sun is down and there's no possibility of being daylit or
            experiencing glare.
    """
    schedule = schedule or generate_default_schedule()
    occ_pattern = [schedule[int(h)] for h in sun_up_hours]
    sun_down_sch = schedule[:]  # copy the schedule in place
    for h in reversed(sun_up_hours):
        sun_down_sch.pop(int(h))
    return occ_pattern, sum(schedule), sum(sun_down_sch)


def _process_input_folder(folder, filter_pattern):
    """Process an annual daylight results folder.

    This returns grids_info and sun-up-hours.
    """
    suh_fp = os.path.join(folder, 'sun-up-hours.txt')
    with open(suh_fp) as suh_file:
        sun_up_hours = [float(hour) for hour in suh_file.readlines()]

    info = os.path.join(folder, 'grids_info.json')
    with open(info) as data_f:
        data = json.load(data_f)

    # filter grids if there is a filtering pattern
    grids = _filter_by_pattern(data, filter=filter_pattern)

    return grids, sun_up_hours


def remove_header(input_file):
    """Remove the header text from a Radiance matrix file."""
    inf = open(input_file)
    first_line = next(inf)
    if first_line[:10] == '#?RADIANCE':
        for line in inf:
            if line[:7] == 'FORMAT=':
                # pass next empty line
                next(inf)
                first_line = next(inf)
                break
            continue
    return first_line, inf
