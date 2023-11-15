# coding=utf-8
from honeybee.properties import ModelProperties, RoomProperties, FaceProperties, \
    ShadeProperties, ApertureProperties, DoorProperties, ShadeMeshProperties
import honeybee.writer.door as door_writer
import honeybee.writer.aperture as aperture_writer
import honeybee.writer.shade as shade_writer
import honeybee.writer.shademesh as shademesh_writer
import honeybee.writer.face as face_writer
import honeybee.writer.room as room_writer
import honeybee.writer.model as model_writer

from .properties.model import ModelRadianceProperties
from .properties.room import RoomRadianceProperties
from .properties.face import FaceRadianceProperties
from .properties.shade import ShadeRadianceProperties
from .properties.shademesh import ShadeMeshRadianceProperties
from .properties.aperture import ApertureRadianceProperties
from .properties.door import DoorRadianceProperties
from .writer import model_to_rad_folder, model_to_rad, room_to_rad, face_to_rad, \
    shade_to_rad, shade_mesh_to_rad, aperture_to_rad, door_to_rad


# set a hidden radiance attribute on each core geometry Property class to None
# define methods to produce radiance property instances on each Property instance
ModelProperties._radiance = None
RoomProperties._radiance = None
FaceProperties._radiance = None
ShadeProperties._radiance = None
ApertureProperties._radiance = None
DoorProperties._radiance = None
ShadeMeshProperties._radiance = None


def model_radiance_properties(self):
    if self._radiance is None:
        self._radiance = ModelRadianceProperties(self.host)
    return self._radiance


def room_radiance_properties(self):
    if self._radiance is None:
        self._radiance = RoomRadianceProperties(self.host)
    return self._radiance


def face_radiance_properties(self):
    if self._radiance is None:
        self._radiance = FaceRadianceProperties(self.host)
    return self._radiance


def shade_radiance_properties(self):
    if self._radiance is None:
        self._radiance = ShadeRadianceProperties(self.host)
    return self._radiance


def aperture_radiance_properties(self):
    if self._radiance is None:
        self._radiance = ApertureRadianceProperties(self.host)
    return self._radiance


def door_radiance_properties(self):
    if self._radiance is None:
        self._radiance = DoorRadianceProperties(self.host)
    return self._radiance


def shade_mesh_radiance_properties(self):
    if self._radiance is None:
        self._radiance = ShadeMeshRadianceProperties(self.host)
    return self._radiance


# add radiance property methods to the Properties classes
ModelProperties.radiance = property(model_radiance_properties)
RoomProperties.radiance = property(room_radiance_properties)
FaceProperties.radiance = property(face_radiance_properties)
ShadeProperties.radiance = property(shade_radiance_properties)
ApertureProperties.radiance = property(aperture_radiance_properties)
DoorProperties.radiance = property(door_radiance_properties)
ShadeMeshProperties.radiance = property(shade_mesh_radiance_properties)

# add energy writer to rad
model_writer.rad_folder = model_to_rad_folder
model_writer.rad = model_to_rad
room_writer.rad = room_to_rad
face_writer.rad = face_to_rad
shade_writer.rad = shade_to_rad
aperture_writer.rad = aperture_to_rad
door_writer.rad = door_to_rad
shademesh_writer.rad = shade_mesh_to_rad
