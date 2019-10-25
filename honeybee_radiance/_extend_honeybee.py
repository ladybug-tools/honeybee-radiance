from honeybee.properties import FaceProperties
import honeybee.writer.face as face_writer
from .properties import FaceRadianceProperties
from .writer import face_to_rad


# add radiance properties to Properties class
def face_radiance_properties(self):
    if self._radiance is None:
        self._radiance = FaceRadianceProperties(self.host)
    return self._radiance


FaceProperties._radiance = None
FaceProperties.radiance = property(face_radiance_properties)

# add radiance writer to idf
face_writer.radiance = face_to_rad
