from abc import ABCMeta, abstractproperty, abstractmethod


class Sky(object):
    """Base class for Honeybee Skies.

    Properties:
        * is_point_in_time
        * is_climate_based
    """
    __metaclass__ = ABCMeta
    __slots__ = ()

    @property
    def is_point_in_time(self):
        """Return True if the sky is generated for a single point in time."""
        return False

    @abstractproperty
    def is_climate_based(self):
        """Return True if the sky is created based on values from weather file."""
        return False

    @classmethod
    def from_dict(cls):
        raise NotImplementedError(
            "from_dict is not implemented for {}.".format(cls.__class__.__name__)
        )

    @abstractmethod
    def to_radiance(self):
        """Return radiance definition as a string."""
        pass

    @abstractmethod
    def to_file(self, file_path):
        """Write sky to file."""
        pass

    def ToString(self):
        """Overwrite .NET ToString method."""
        return self.__repr__()

    def __repr__(self):
        """Sky representation."""
        return self.to_radiance()
