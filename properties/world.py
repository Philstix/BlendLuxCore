import bpy
import math
from bpy.props import (
    PointerProperty, EnumProperty, FloatProperty,
    FloatVectorProperty, IntProperty, BoolProperty
)
from .light import (
    SAMPLES_DESCRIPTION, IMPORTANCE_DESCRIPTION,
    GAMMA_DESCRIPTION, SAMPLEUPPERHEMISPHEREONLY_DESCRIPTION,
    VISIBILITYMAP_ENABLE_DESC,
)


def init():
    bpy.types.World.luxcore = PointerProperty(type=LuxCoreWorldProps)


class LuxCoreWorldProps(bpy.types.PropertyGroup):
    lights = [
        ("sky2", "Sky", "Hosek and Wilkie sky model", 0),
        ("infinite", "HDRI", "High dynamic range image", 1),
        ("constantinfinite", "Flat Color", "Flat background color", 2),
        ("none", "None", "No background light", 3),
    ]
    light = EnumProperty(name="Background", items=lights, default="sky2")

    # Generic properties shared by all background light types
    gain = FloatProperty(name="Gain", default=1, min=0, description="Brightness multiplier")
    rgb_gain = FloatVectorProperty(name="Tint", default=(1, 1, 1), min=0, max=1, subtype="COLOR")
    samples = IntProperty(name="Samples", default=-1, min=-1, description=SAMPLES_DESCRIPTION)
    importance = FloatProperty(name="Importance", default=1, min=0, description=IMPORTANCE_DESCRIPTION)
    # TODO: id

    # sky2 settings
    sun = PointerProperty(name="Sun", type=bpy.types.Object, description="Used to specify the sun direction")
    turbidity = FloatProperty(name="Turbidity", default=2.2, min=0, max=30)
    groundalbedo = FloatVectorProperty(name="Ground Albedo", default=(0.5, 0.5, 0.5), min=0, max=1, subtype="COLOR")
    ground_enable = BoolProperty(name="Use Ground Color", default=False)
    ground_color = FloatVectorProperty(name="Ground Color", default=(0.5, 0.5, 0.5), min=0, max=1, subtype="COLOR")

    # infinite
    image = PointerProperty(name="Image", type=bpy.types.Image)
    gamma = FloatProperty(name="Gamma", default=1, min=0, description=GAMMA_DESCRIPTION)
    sampleupperhemisphereonly = BoolProperty(name="Sample Upper Hemisphere Only", default=False,
                                             description=SAMPLEUPPERHEMISPHEREONLY_DESCRIPTION)
    rotation = FloatProperty(name="Z Axis Rotation", default=0, min=0, max=(math.pi * 2), subtype="ANGLE", unit="ROTATION")

    # sky2, sun, infinite, constantinfinite
    visibility_indirect_diffuse = BoolProperty(name="Diffuse", default=True)
    visibility_indirect_glossy = BoolProperty(name="Glossy", default=True)
    visibility_indirect_specular = BoolProperty(name="Specular", default=True)

    # sky2, infinite, constantinfinite
    visibilitymap_enable = BoolProperty(name="Build Visibility Map", default=True,
                                        description=VISIBILITYMAP_ENABLE_DESC)

    volume = PointerProperty(type=bpy.types.NodeTree)
