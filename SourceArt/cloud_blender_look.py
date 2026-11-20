# Creates an unlit, flat, semi-transparent cloud material that mimics the
# Blender viewport look, and assigns it to the imported Layer1 cloud meshes.
import unreal

AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary

PKG = "/Game/Layer1/Materials"
M_NAME = "M_Cloud_BlenderLook"
MI_NAME = "MI_Cloud_BlenderLook"
CLOUD_MESHES = [
    "/Game/Layer1/Layer1_NoSun/StaticMeshes/Canopy___Continuous_mesh___80k_002",
    "/Game/Layer1/Layer1_NoSun/StaticMeshes/Canopy___Continuous_mesh___80k_003",
]


def srgb_to_linear(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin_color(r, g, b):
    return unreal.LinearColor(srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), 1.0)


# ---- master material -------------------------------------------------------
m_path = f"{PKG}/{M_NAME}"
if EAL.does_asset_exist(m_path):
    m = unreal.load_asset(m_path)
    MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset(M_NAME, PKG, unreal.Material, unreal.MaterialFactoryNew())

m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("two_sided", True)

color = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -700, -100)
color.set_editor_property("parameter_name", "CloudColor")
color.set_editor_property("default_value", lin_color(70, 88, 108))

bright = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -700, 100)
bright.set_editor_property("parameter_name", "Brightness")
bright.set_editor_property("default_value", 1.0)

mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 0)
MEL.connect_material_expressions(color, "", mul, "A")
MEL.connect_material_expressions(bright, "", mul, "B")
MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

opacity = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -700, 300)
opacity.set_editor_property("parameter_name", "Opacity")
opacity.set_editor_property("default_value", 0.65)
MEL.connect_material_property(opacity, "", unreal.MaterialProperty.MP_OPACITY)

MEL.recompile_material(m)
EAL.save_asset(m_path, only_if_is_dirty=False)

# ---- material instance (tweak this one) -------------------------------------
mi_path = f"{PKG}/{MI_NAME}"
if EAL.does_asset_exist(mi_path):
    mi = unreal.load_asset(mi_path)
else:
    mi = AT.create_asset(MI_NAME, PKG, unreal.MaterialInstanceConstant,
                         unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m)
MEL.update_material_instance(mi)
EAL.save_asset(mi_path, only_if_is_dirty=False)

# ---- assign to cloud meshes and their actors in the open level --------------
meshes = []
for p in CLOUD_MESHES:
    sm = unreal.load_asset(p)
    if sm is None:
        print("CLOUDLOOK missing mesh", p)
        continue
    for i in range(len(sm.get_editor_property("static_materials"))):
        sm.set_material(i, mi)
    EAL.save_asset(p, only_if_is_dirty=False)
    meshes.append(sm)

n = 0
for comp in unreal.EditorLevelLibrary.get_all_level_actors_components():
    if isinstance(comp, unreal.StaticMeshComponent) and comp.static_mesh in meshes:
        for i in range(comp.get_num_materials()):
            comp.set_material(i, mi)
        n += 1

print(f"CLOUDLOOK done: meshes={len(meshes)} components={n}")
