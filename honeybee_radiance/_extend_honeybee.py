from honeybee.properties import Properties
import honeybee.writer as writer
from .properties import RadianceProperties
from .writer import face_to_rad

# add radiance properties to Properties class
Properties.radiance = property(lambda self: RadianceProperties(
    self.face_type, self.boundary_condition))

# add radiance writer to idf
setattr(writer, 'radiance', face_to_rad)
