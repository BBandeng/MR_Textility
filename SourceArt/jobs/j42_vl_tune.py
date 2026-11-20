import unreal
MEL = unreal.MaterialEditingLibrary
mi = unreal.load_asset("/Game/PaintClouds/MI_VolCloudLayers")
P = {"NoiseLow": 0.62, "NoiseHigh": 0.9, "Coverage": 0.45, "WarmGlowStrength": 0.08, "DensityScale": 0.03, "EdgeSharpness": 6.0}
for k, v in P.items():
    MEL.set_material_instance_scalar_parameter_value(mi, k, v)
MEL.update_material_instance(mi); unreal.EditorAssetLibrary.save_asset(mi.get_path_name(), only_if_is_dirty=False)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=12, yaw=0))
print("VLT", P)
