"""Utilities to determine the path of light taken through interior spaces of a model."""
from honeybee.boundarycondition import Surface
from honeybee.facetype import AirBoundary


def light_path_from_room(model, room_identifier, static_name='__static_apertures__'):
    """Get the dynamic aperture groups that need to be simulated for a room in a model.
    
    Args:
        model: A honeybee Model object which will be used to identify the aperture
            groups that are needed to simulate a single room.
        room_identifier: Text string for the identifier of the Room in the model
            for which the light path will be computed.
        static_name: An optional name to be used to refer to static apertures
            found within the model. (Default: '__static_apertures__').

    Returns:
        A list of lists where each sub-list contains the identifiers of the aperture
        groups through which light is passing

    Usage:

    .. code-block:: python

        from honeybee_radiance.lightpath import light_path_from_room
        from honeybee.room import Room
        from honeybee.model import Model
        from ladybug_geometry.geometry3d.pointvector import Point3D

        room1 = Room.from_box('Tiny_House_Room1', 5, 10, 3)
        room1[2].apertures_by_ratio(0.4, 0.01)  # east interior window
        room1[3].apertures_by_ratio(0.4, 0.01)  # outdoor south window
        south_ap1 = room1[3].apertures[0]
        south_ap1.properties.radiance.dynamic_group_identifier = 'SouthWindow1'

        room2 = Room.from_box('Tiny_House_Room2', 5, 10, 3, origin=Point3D(5, 0, 0))
        room2[4].apertures_by_ratio(0.4, 0.01)  # west interior window
        room2[1].apertures_by_ratio(0.4, 0.01)  # outdoor north window
        north_ap2 = room2[1].apertures[0]
        north_ap2.properties.radiance.dynamic_group_identifier = 'NorthWindow2'

        Room.solve_adjacency([room1, room2], 0.01)
        model = Model('TinyHouse', [room1, room2])

        print(light_path_from_room(model, room1.identifier))

        >> [['SouthWindow1'], ['__static_apertures__', 'NorthWindow2']]
    """
    def _get_room_light_path(model, room_identifier, static_name):
        # get the Room object from the Model
        room = model.rooms_by_identifier([room_identifier])[0]

        # gather all of the dynamic groups that the Room has in its apertures
        grp_ids = set()
        adj_rooms = set()
        for face in room.faces:
            for s_face in face.apertures + face.doors:
                if s_face.properties.radiance._dynamic_group_identifier:
                    grp_id = s_face.properties.radiance._dynamic_group_identifier
                else:
                    grp_id = static_name
                if isinstance(s_face.boundary_condition, Surface):
                    adj_room = s_face.boundary_condition.boundary_condition_objects[-1]
                    adj_rooms.add((grp_id, adj_room))
                else:
                    grp_ids.add(grp_id)

        # if there are no interior apertures, return the list as it is
        light_path = [[grp_id] for grp_id in grp_ids]
        if len(adj_rooms) == 0:
            return room, light_path

        # loop through adjacent rooms and gather their aperture groups
        # TODO: Make this part recursive to trace the light path more than one room away.
        room_objs = model.rooms_by_identifier([room_tup[1] for room_tup in adj_rooms])
        for room_obj, room_tup in zip(room_objs, adj_rooms):
            rm_grp_ids = set()
            for face in room_obj.faces:
                for s_face in face.apertures + face.doors:
                    if s_face.properties.radiance._dynamic_group_identifier:
                        rm_grp_ids.add(s_face.properties.radiance._dynamic_group_identifier)
                    else:
                        rm_grp_ids.add(static_name)
            base_grp_id = room_tup[0]
            for g_id in rm_grp_ids:
                if g_id != base_grp_id:  # group has already been accounted for
                    light_path.append([base_grp_id, g_id])
            if (len(rm_grp_ids) == 1 and static_name in rm_grp_ids and
                not static_name in grp_ids):
                light_path.append([static_name])

        return room, light_path

    room, light_path = _get_room_light_path(model, room_identifier, static_name)

    air_boundary_rooms = set()
    # rooms with air boundaries should inherit the light path of rooms adjacent
    # to the air boundary
    def _check_air_boundary(model, room, light_path, static_name):
        air_boundary_rooms.add(room.identifier)
        for face in room.faces:
            if isinstance(face.type, AirBoundary):
                adj_room = face.boundary_condition.boundary_condition_objects[-1]
                if not adj_room in air_boundary_rooms:
                    air_boundary_rooms.add(adj_room)
                    room, lp = _get_room_light_path(model, adj_room, static_name)
                    light_path.extend(lp)
                    _check_air_boundary(model, room, light_path, static_name)

    _check_air_boundary(model, room, light_path, static_name)

    return light_path
