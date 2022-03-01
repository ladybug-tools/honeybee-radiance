"""Functions for post-processing daylight outputs into electric lighting schedules."""
import os

from .annualdaylight import generate_default_schedule, _process_input_folder


def daylight_control_schedules(
    results_folder, base_schedule=None, ill_setpoint=300,
    min_power_in=0.3, min_light_out=0.2, off_at_min=False
):
    """Generate electric lighting schedules from annual daylight results.

    Such controls will dim the lights according to whether the illuminance values
    at the sensor locations are at a target illuminance setpoint. The results can be
    used to account for daylight controls in energy simulations.

    This function will generate one schedule per sensor grid in the simulation. Each
    grid should have sensors at the locations in space where daylight dimming sensors
    are located. Grids with one, two, or more sensors can be used to model setups
    where fractions of each room are controlled by different sensors. If the sensor
    grids are distributed over the entire floor of the rooms, the resulting schedules
    will be idealized, where light dimming has been optimized to supply the minimum
    illuminance setpoint everywhere in the room.

    Args:
        results_folder: The path to the folder containing the annual daylight
            result files.
        base_schedule: A list of 8760 fractional values for the lighting schedule
            representing the usage of lights without any daylight controls. The
            values of this schedule will be multiplied by the hourly dimming
            fraction to yield the output lighting schedules. If None, a schedule
            from 9AM to 5PM on weekdays will be used. (Default: None).
        ill_setpoint: A number for the illuminance setpoint in lux beyond which
            electric lights are dimmed if there is sufficient daylight.
            Some common setpoints are listed below. (Default: 300 lux).

            * 50 lux - Corridors and hallways.
            * 150 lux - Computer work spaces (screens provide illumination).
            * 300 lux - Paper work spaces (reading from surfaces that need illumination).
            * 500 lux - Retail spaces or museums illuminating merchandise/artifacts.
            * 1000 lux - Operating rooms and workshops where light is needed for safety.

        min_power_in: A number between 0 and 1 for the the lowest power the lighting
            system can dim down to, expressed as a fraction of maximum
            input power. (Default: 0.3).
        min_light_out: A number between 0 and 1 the lowest lighting output the lighting
            system can dim down to, expressed as a fraction of maximum light
            output. Note that setting this to 1 means lights aren't dimmed at
            all until the illuminance setpoint is reached. This can be used to
            approximate manual light-switching behavior when used in conjunction
            with the off_at_min input below. (Default: 0.2).
        off_at_min: Boolean to note whether lights should switch off completely when
            they get to the minimum power input. (Default: False).

    Returns:
        A tuple with two values.

        -   schedules: A list of lists where each sub-list represents an electric
            lighting dimming schedule for a sensor grid.

        -   schedule_ids: A list of text strings for the recommended names of the
            electric lighting schedules.
    """
    # process the base schedule input into a list of values
    if base_schedule is None:
        base_schedule = generate_default_schedule()

    # get the relevant .ill files
    grids, sun_up_hours = _process_input_folder(results_folder, '*')
    sun_up_hours = [int(h) for h in sun_up_hours]

    # get the dimming fractions for each sensor grid from the .ill files
    dim_fracts = []
    for grid_info in grids:
        ill_file = os.path.join(results_folder, '%s.ill' % grid_info['full_id'])
        fract_list = _file_to_dimming_fraction(
            ill_file, sun_up_hours, ill_setpoint, min_power_in,
            min_light_out, off_at_min
        )
        dim_fracts.append(fract_list)

    # create the schedule by combining the base schedule with the dimming fraction
    schedules, schedule_ids = [], []
    for grid_info, dim_fract in zip(grids, dim_fracts):
        sch_vals = [b_val * d_val for b_val, d_val in zip(base_schedule, dim_fract)]
        sch_id = '{} Daylight Control'.format(grid_info['full_id'])
        schedules.append(sch_vals)
        schedule_ids.append(sch_id)
    return schedules, schedule_ids


def _file_to_dimming_fraction(ill_file, su_pattern, setpt, m_pow, m_lgt, off_m):
    """Compute hourly dimming fractions for a given result file."""
    # get a base schedule of dimming fractions for the sun-up hours
    su_values = [0] * len(su_pattern)
    sensor_count = 0
    with open(ill_file) as results:
        for pt_res in results:
            sensor_count += 1
            for i, val in enumerate(pt_res.split()):
                su_values[i] += _dimming_from_ill(float(val), setpt, m_pow, m_lgt, off_m)
    su_values = [val / sensor_count for val in su_values]

    # account for the hours where the sun is not up
    dim_fract = [1] * 8760
    for val, hr in zip(su_values, su_pattern):
        dim_fract[hr] = float(val)
    return dim_fract


def _dimming_from_ill(ill_val, ill_setpt, min_pow, min_light, off_at_min):
    """Compute the dimming fraction from an illuminance value."""
    if ill_val > ill_setpt:  # dimmed all of the way
        return 0 if off_at_min else min_pow
    elif ill_val <= min_light:  # not dimmed at all
        return 1
    else:  # partially dimmed
        fract_dim = (ill_setpt - ill_val) / (ill_setpt - min_light)
        return fract_dim + ((1 - fract_dim) * min_pow)
