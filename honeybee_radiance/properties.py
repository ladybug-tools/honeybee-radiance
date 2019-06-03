"""Radiance Properties."""
from .material.materialbase import Material


class RadianceProperties(object):
    """Radiance Properties for Honeybee geometry."""

    def __init__(self, face_type, boundary_condition):
        self._face_type = face_type
        self._boundary_condition = boundary_condition
        # this will be set by user
        self._modifier = None
        self._modifier_dir = None
        # this will be set by parent zone
        self._modifierset = None

    @property
    def modifier(self):
        """Set or get Face material.

        If material is not set by user then it will be assigned based on parent zone
        material-set when the face is added to a zone.
        """
        if self._modifier:
            # set by user
            return self._modifier
        elif self._modifierset:
            # set by parent zone
            return self._modifierset(self._face_type, self._boundary_condition)
        else:
            return None

    @modifier.setter
    def modifier(self, value):
        if value:
            assert isinstance(value, Material), \
                'Expected Radiance modifier not {}'.format(type(value))
        self._modifier = value

    @property
    def is_modifier_set_by_user(self):
        """Check if construction is set by user."""
        return self._modifier is not None

    @property
    def is_modifier_set_by_zone(self):
        """Check if construction is set by user."""
        return not self.is_modifier_set_by_user \
            and self._modifierset is not None

    @property
    def modifier_dir(self):
        """Radiance modifier for direct sunlight studies."""
        return self._modifier_dir

    @modifier_dir.setter
    def modifier_dir(self, value):
        if value:
            assert isinstance(value, Material), \
                'Expected Radiance modifier not {}'.format(type(value))
        self._modifier_dir = value

    def to_dict(self):
        """Return radiance properties as a dictionary."""
        base = {'radiance': {}}
        base['radiance']['modifier'] = self.modifier.to_dict if self.modifier else None
        base['radiance']['modifier_dir'] = \
            self.modifier_dir.to_dict if self.modifier_dir else None
        # modifier set should be set to generic if not set by user
        base['radiance']['modifier_set'] = \
            self._modifierset.name if self._modifierset else None
        return base

    def __repr__(self):
        return 'RadianceProperties'
