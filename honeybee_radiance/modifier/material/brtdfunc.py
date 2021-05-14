"""Radiance BRTDfunc Material.

http://radsite.lbl.gov/radiance/refer/ray.html#BRTDfunc
"""
from .materialbase import Material


# TODO: Implement the class. It's currently only a generic Radiance Primitive
class BRTDfunc(Material):
    """Radiance BRTDfunc Material.

    The material BRTDfunc gives the maximum flexibility over surface reflectance and
    transmittance, providing for spectrally-dependent specular rays and reflectance and
    transmittance distribution functions.

    .. code-block:: shell

        mod BRTDfunc id
        10+  rrefl  grefl  brefl
             rtrns  gtrns  btrns
             rbrtd  gbrtd  bbrtd
             funcfile  transform
        0
        9+   rfdif gfdif bfdif
             rbdif gbdif bbdif
             rtdif gtdif btdif
             A10 ..

    The variables rrefl, grefl and brefl specify the color coefficients for the ideal
    specular (mirror) reflection of the surface. The variables rtrns, gtrns and btrns
    specify the color coefficients for the ideal specular transmission. The functions
    rbrtd, gbrtd and bbrtd take the direction to the incident light (and its solid angle)
    and compute the color coefficients for the directional diffuse part of reflection and
    transmission. As a special case, three identical values of '0' may be given in place
    of these function names to indicate no directional diffuse component.

    Unlike most other material types, the surface normal is not altered to face the
    incoming ray. Thus, functions and variables must pay attention to the orientation of
    the surface and make adjustments appropriately. However, the special variables for
    the perturbed dot product and surface normal, RdotP, NxP, NyP and NzP are reoriented
    as if the ray hit the front surface for convenience.

    A diffuse reflection component may be given for the front side with rfdif, gfdif and
    bfdif for the front side of the surface or rbdif, gbdif and bbdif for the back side.
    The diffuse transmittance (must be the same for both sides by physical law) is given
    by rtdif, gtdif and btdif. A pattern will modify these diffuse scattering values, and
    will be available through the special variables CrP, CgP and CbP.

    Care must be taken when using this material type to produce a physically valid
    reflection model. The reflectance functions should be bidirectional, and under no
    circumstances should the sum of reflected diffuse, transmitted diffuse, reflected
    specular, transmitted specular and the integrated directional diffuse component be
    greater than one.

    Args:
        identifier: Text string for a unique Material ID. Must not contain spaces
            or special characters. This will be used to identify the object across
            a model and in the exported Radiance files.
        modifier: Modifier. It can be primitive, mixture, texture or pattern.
            (Default: None).
        values: An array 3 arrays for primitive data. Each of the 3 sub-arrays
            refer to a line number in the radiance primitive definitions and the
            values in each array correspond to values occurring within each line.
        is_opaque: A boolean to indicate whether this primitive is opaque.
        dependencies: A list of primitives that this primitive depends on. This
            argument is only useful for defining advanced primitives that are
            defined based on other primitives. (Default: []).

    Properties:
        * identifier
        * display_name
        * values
        * modifier
        * dependencies
        * is_modifier
        * is_material
        * is_opaque
    """
    __slots__ = ()

    pass
