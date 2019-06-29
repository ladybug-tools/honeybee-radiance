from .optionbase import BoolOption
from .rcontrib import RcontribOptions
import honeybee_radiance.exception as exceptions


class RfluxmtxOptions(RcontribOptions):
    """rcontrib command options."""

    __slots__ = ('_v',)

    def __init__(self):
        """rcontrib command options."""
        RcontribOptions.__init__(self)
        self._on_setattr_check = False
        self._v = BoolOption('v', 'verbose report - default: off')
        self._protected = ('f', 'e', 'p', 'b', 'bn', 'm', 'M')
        self._on_setattr_check = True

    def on_setattr(self):
        RcontribOptions.on_setattr(self)
        for opt in self._protected:
             if getattr(self, opt).is_set:
                raise exceptions.ProtectedOptionError('rfluxmtx', opt)

    @property
    def v(self):
        """output coefficients - default: off"""
        return self._v

    @v.setter
    def v(self, value):
        self._v.value = value
