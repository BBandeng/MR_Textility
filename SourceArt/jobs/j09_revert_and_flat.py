# 1) Reverts the volumetric-cloud experiment in the open level.
# 2) Applies a flat, unlit, semi-transparent material to the Layer1 cloud meshes
#    (matches the Blender viewport screenshot).
import unreal

AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

# ---------------------------------------------------------------- revert
for a in list(EAS.get_all_level_actors()):
    cls = a.get_class().get_name()
    label = a.get_actor_label()
    if cls == "BP_HeavenClouds_C" or label == "HeavenClouds":
        EAS.destroy_actor(a); print("RV removed HeavenClouds actor")
    elif cls == "SkyAtmosphere":
        a.set_actor_location(unreal.Vector(0, 0, -6000), False, False); print("RV skyatmo z=-6000")
    elif cls == "VolumetricCloud":
        a.get_component_by_class(unreal.VolumetricCloudComponent).set_visibility(True)
        a.set_actor_hidden_in_game(False); print("RV default cloud visible")
    elif label == "Floor":
        a.get_component_by_class(unreal.StaticMeshComponent).set_visibility(True)
        a.set_actor_hidden_in_game(False); print("RV floor visible")
    elif cls == "StaticMeshActor":
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh and "Canopy" in c.static_mesh.get_name():
            c.set_visibility(True); a.set_actor_hidden_in_game(False)
            c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            print("RV canopy visible", label)

# ---------------------------------------------------------------- flat material
PKG = "/Game/Layer1/Materials"

def s2l(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

m_path = f"{PKG}/M_Cloud_BlenderLook"
if EAL.does_asset_exist(m_path):
    m = unreal.load_asset(m_path); MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_Cloud_BlenderLook", PKG, unreal.Material, unreal.MaterialFactoryNew())
m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
m.set_editor_property("two_sided", True)

color = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, 0)
color.set_editor_property("parameter_name", "CloudColor")
color.set_editor_property("default_value", unreal.LinearColor(s2l(69), s2l(90), s2l(119), 1.0))
MEL.connect_material_property(color, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
op = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, 250)
op.set_editor_property("parameter_name", "Opacity")
op.set_editor_property("default_value", 0.6)
MEL.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
MEL.recompile_material(m)
EAL.save_asset(m_path, only_if_is_dirty=False)

mi_path = f"{PKG}/MI_Cloud_BlenderLook"
mi = unreal.load_asset(mi_path) if EAL.does_asset_exist(mi_path) else AT.create_asset(
    "MI_Cloud_BlenderLook", PKG, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m)
MEL.update_material_instance(mi)
EAL.save_asset(mi_path, only_if_is_dirty=False)

n = 0
for a in EAS.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh and "Canopy" in c.static_mesh.get_name():
            for i in range(c.get_num_materials()):
                c.set_material(i, mi)
            c.set_cast_shadow(False)
            n += 1
print("FLAT done components=", n)
