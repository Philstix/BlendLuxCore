import bpy
from bpy.props import BoolProperty
from .. import LuxCoreNodeMaterial, Roughness


IOR_DESCRIPTION = "Specify index of refraction to control reflection brightness"

MULTIBOUNCE_DESCRIPTION = (
    "Gives the material a fuzzy sheen and makes it look "
    "like it is coated in fine dust"
)


class LuxCoreNodeMatGlossyTranslucent(LuxCoreNodeMaterial):
    bl_label = "Glossy Translucent Material"
    bl_width_min = 160

    def update_use_ior(self, context):
        self.inputs["IOR"].enabled = self.use_ior

    def update_use_ior_bf(self, context):
        self.inputs["BF IOR"].enabled = self.use_ior_bf

    def update_use_backface(self, context):
        # Note: these are the names (strings), not references to the sockets
        sockets = [socket for socket in self.inputs.keys() if socket.startswith("BF ")]

        for socket in sockets:
            if socket == "BF V-Roughness":
                self.inputs[socket].enabled = self.use_backface and self.use_anisotropy
            elif socket == "BF IOR":
                self.inputs[socket].enabled = self.use_backface and self.use_ior_bf
            else:
                self.inputs[socket].enabled = self.use_backface

    # This enables/disables anisotropic roughness for both front and back face
    use_anisotropy = BoolProperty(name=Roughness.aniso_name,
                                  default=False,
                                  description=Roughness.aniso_desc,
                                  update=Roughness.update_anisotropy)

    # Front face
    multibounce = BoolProperty(name="Multibounce", default=False,
                               description=MULTIBOUNCE_DESCRIPTION)
    use_ior = BoolProperty(name="Use IOR", default=False,
                           update=update_use_ior,
                           description=IOR_DESCRIPTION)

    # Back face
    use_backface = BoolProperty(name="Double Sided", default=False,
                                update=update_use_backface,
                                description="Enable if used on a 2D mesh, e.g. on tree leaves")
    multibounce_bf = BoolProperty(name="BF Multibounce", default=False,
                                  description=MULTIBOUNCE_DESCRIPTION + " (backface)")
    use_ior_bf = BoolProperty(name="BF Use IOR", default=False,
                              update=update_use_ior_bf,
                              description=IOR_DESCRIPTION + " (backface)")

    def init(self, context):
        default_roughness = 0.05

        self.add_input("LuxCoreSocketColor", "Diffuse Color", [0.5] * 3)
        self.add_input("LuxCoreSocketColor", "Transmission Color", [0.5] * 3)

        # Front face
        self.add_input("LuxCoreSocketColor", "Specular Color", [0.05] * 3)
        self.add_input("LuxCoreSocketIOR", "IOR", 1.5)
        self.inputs["IOR"].enabled = False
        self.add_input("LuxCoreSocketColor", "Absorption Color", [0] * 3)
        self.add_input("LuxCoreSocketFloatPositive", "Absorption Depth (nm)", 0)
        Roughness.init(self, default_roughness)

        # Back face
        self.add_input("LuxCoreSocketColor", "BF Specular Color", [0.05] * 3)
        self.add_input("LuxCoreSocketIOR", "BF IOR", 1.5)
        self.inputs["BF IOR"].enabled = False
        self.add_input("LuxCoreSocketColor", "BF Absorption Color", [0] * 3)
        self.add_input("LuxCoreSocketFloatPositive", "BF Absorption Depth (nm)", 0)
        Roughness.init_backface(self, default_roughness, init_enabled=False)

        self.add_common_inputs()

        self.outputs.new("LuxCoreSocketMaterial", "Material")

    def draw_buttons(self, context, layout):
        layout.prop(self, "multibounce")
        layout.prop(self, "use_ior")
        Roughness.draw(self, context, layout)

        layout.prop(self, "use_backface", toggle=True)

        if self.use_backface:
            layout.prop(self, "multibounce_bf")
            layout.prop(self, "use_ior_bf")

    def export(self, props, luxcore_name=None):
        definitions = {
            "type": "glossytranslucent",
            "kd": self.inputs["Diffuse Color"].export(props),
            "kt": self.inputs["Transmission Color"].export(props),

            # Front face (in normal direction)
            "multibounce": self.multibounce,
            "ks": self.inputs["Specular Color"].export(props),
            "ka": self.inputs["Absorption Color"].export(props),
            "d": self.inputs["Absorption Depth (nm)"].export(props),
        }

        if self.use_ior:
            definitions["index"] = self.inputs["IOR"].export(props)

        if self.use_backface:
            definitions.update({
                # Back face (on opposite side of normal)
                "multibounce_bf": self.multibounce_bf,
                "ks_bf": self.inputs["BF Specular Color"].export(props),
                "ka_bf": self.inputs["BF Absorption Color"].export(props),
                "d_bf": self.inputs["BF Absorption Depth (nm)"].export(props),
            })

            if self.use_ior_bf:
                definitions["index_bf"] = self.inputs["BF IOR"].export(props)

        # This includes backface roughness
        Roughness.export(self, props, definitions)
        self.export_common_inputs(props, definitions)
        return self.base_export(props, definitions, luxcore_name)
