"""Radiance Texdata Texture.

A texture is a perturbation of the surface normal, and is given by either a function or
data.

http://radsite.lbl.gov/radiance/refer/ray.html#Texdata
"""
from .texturebase import Texture


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class Texdata(Texture):
    """Radiance Texdata Material.

    A texdata texture uses three data files to get the surface normal perturbations. The
    variables xfunc, yfunc and zfunc take three arguments each from the interpolated
    values in xdfname, ydfname and zdfname.

    .. code-block:: shell

        mod texdata id
        8+ xfunc yfunc zfunc xdfname ydfname zdfname vfname x0 x1 .. xf
        0
        n A1 A2 .. An

    """
    __slots__ = ()

    pass
