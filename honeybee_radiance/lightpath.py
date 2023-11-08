"""Utilities to determine the path of light taken through interior spaces of a model."""
from honeybee.boundarycondition import Surface, Outdoors
from honeybee.facetype import AirBoundary
from honeybee.aperture import Aperture
from honeybee.door import Door


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
    #TODO: Consider to modify light path if there are two consecutive
    #      items, such as ['__static_apertures__', '__static_apertures__'].
    def get_adjacent_room(face):
        """Get the adjacent Room of a Face.

        Args:
            face: A Face object for which to find the adjacent room.

        Returns:
            A Room object.
        """
        adj_room_identifier = \
            face.boundary_condition.boundary_condition_objects[-1]
        adj_room = model.rooms_by_identifier([adj_room_identifier])[0]

        return adj_room

    def trace_light_path(
            s_face, s_light_path, parent_room, passed_rooms = set(),
            static_name='__static_apertures__'):
        """Trace light path recursively.
        
        This function will return the light path for a single face (Aperture,
        Door, or AirBoundary). The function will trace the light path
        recursively meaning that it will enter rooms adjacent to interior
        Apertures and Doors as well as AirBoundaries.

        Args:
            s_face: The Aperture, Door, or AirBoundary for which to trace the
                light path.
            s_light_path: The base light path of the s_face. This is a single
                item list which contains the dynamic group identifier or the
                static name, however, if s_face is an AirBoundary the list will
                be empty.
            parent_room: A Room object. This Room is the parent Room of the
                s_face. In this function the parent room is used to check that
                we do not go back into the parent room, and enter a infinite
                recursive loop.
            passed_rooms: A set of Room objects. This set contains the rooms
                that have already been processed. This is used to not enter an
                infinite recursive loop, e.g., if multiple are connected by
                interior apertures.
            static_name: An optional name to be used to refer to static apertures
                found within the model. (Default: '__static_apertures__').
        
        Returns:
            A list of lists where each sub-list contains the identifiers of the
            ApertureGroups through which light is passing.
        """
        passed_rooms.add(parent_room)
        s_face_light_path = []
        room = get_adjacent_room(s_face)
        for face in room.faces:
            adj_s_faces = face.apertures + face.doors
            if isinstance(face.type, AirBoundary):
                adj_s_faces = adj_s_faces + (face,)
            for adj_s_face in adj_s_faces:
                s_light_path_duplicate = list(s_light_path)
                if isinstance(adj_s_face, (Aperture, Door)):
                    if adj_s_face.properties.radiance._dynamic_group_identifier:
                        light_path_id = \
                            adj_s_face.properties.radiance._dynamic_group_identifier
                    else:
                        light_path_id = static_name
                if isinstance(adj_s_face.boundary_condition, Surface):
                    adj_room = get_adjacent_room(adj_s_face)
                    # check that adjacent room is not in passed_rooms
                    if not adj_room in passed_rooms:
                        if isinstance(adj_s_face, (Aperture, Door)):
                            # do not append if face is an AirBoundary
                            if not s_light_path_duplicate:
                                s_light_path_duplicate.append(light_path_id)
                            elif not light_path_id == s_light_path_duplicate[-1]:
                                s_light_path_duplicate.append(light_path_id)
                        _s_face_light_path = trace_light_path(
                            adj_s_face, s_light_path_duplicate, room,
                            passed_rooms=passed_rooms
                        )
                        s_face_light_path.extend(_s_face_light_path)
                elif not isinstance(adj_s_face, (Aperture, Door)) and \
                    isinstance(adj_s_face.boundary_condition, Outdoors):
                    # if not Aperture or Door (i.e. AirBoundary), we just pass
                    # if the boundary condition is Outdoors
                    pass
                else:
                    if not s_light_path_duplicate:
                        s_light_path_duplicate.append(light_path_id)
                    elif not light_path_id == s_light_path_duplicate[-1]:
                        s_light_path_duplicate.append(light_path_id)
                    if s_light_path_duplicate not in s_face_light_path:
                        s_face_light_path.append(s_light_path_duplicate)

        return s_face_light_path

    _light_path = []
    room = model.rooms_by_identifier([room_identifier])[0]
    for face in room.faces:
        s_faces = face.apertures + face.doors
        if isinstance(face.type, AirBoundary):
            s_faces = s_faces + (face,)
        for s_face in s_faces:
            if isinstance(s_face, (Aperture, Door)):
                # create base light path if Aperture or Door
                if s_face.properties.radiance._dynamic_group_identifier:
                    s_light_path = \
                        [s_face.properties.radiance._dynamic_group_identifier]
                else:
                    s_light_path = [static_name]
            else:
                # else AirBoundary, no light path id
                s_light_path = []
            if isinstance(s_face.boundary_condition, Surface):
                # boundary condition, trace light path recursively for s_face
                s_face_light_path = \
                    trace_light_path(s_face, s_light_path, room)
                _light_path.extend(s_face_light_path)
            elif not isinstance(s_face, (Aperture, Door)):
                # if it is AirBoundary but without Surface boundary condition
                pass
            else:
                # no boundary condition, tracing ends here
                if not s_light_path in _light_path:
                    _light_path.append(s_light_path)

    # remove any duplicates
    light_path = []
    for lp in _light_path:
        if not lp in light_path:
            light_path.append(lp)

    return light_path
