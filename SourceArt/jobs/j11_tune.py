import unreal
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
def s2l(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
m = unreal.load_asset("/Game/Layer1/Materials/M_Cloud_BlenderLook")
print("TUNE fogprops", [n for n in dir(m) if "fog" in n.lower()])
for n in ["apply_fogging", "apply_cloud_fogging"]:
    try:
        m.set_editor_property(n, False); print("TUNE off", n)
    except Exception as e:
        print("TUNE fail", n, repr(e))
MEL.recompile_material(m)
EAL.save_asset(m.get_path_name(), only_if_is_dirty=False)
mi = unreal.load_asset("/Game/Layer1/Materials/MI_Cloud_BlenderLook")
MEL.set_material_instance_vector_parameter_value(mi, "CloudColor", unreal.LinearColor(s2l(72), s2l(86), s2l(104), 1.0))
MEL.set_material_instance_scalar_parameter_value(mi, "Opacity", 0.62)
MEL.update_material_instance(mi)
EAL.save_asset(mi.get_path_name(), only_if_is_dirty=False)
print("TUNE done")
