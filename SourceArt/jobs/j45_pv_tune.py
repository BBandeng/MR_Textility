import unreal
MEL = unreal.MaterialEditingLibrary
mi = unreal.load_asset("/Game/PaintClouds/MI_PaintVolCloud")
P = {"L1_Cover": 0.34, "L2_Cover": 0.16, "L3_Cover": 0.3, "L4_Cover": 0.38, "NoiseLow": 0.62, "NoiseHigh": 0.92,
     "ShapeScale": 3200.0, "BillowScale": 1000.0, "DetailScale": 260.0, "DetailErosion": 0.3,
     "GlowStrength": 0.12, "DensityScale": 0.035, "EdgeSharpness": 9.0, "ClearInner": 60.0, "ClearOuter": 300.0}
for k, v in P.items():
    MEL.set_material_instance_scalar_parameter_value(mi, k, v)
MEL.update_material_instance(mi); unreal.EditorAssetLibrary.save_asset(mi.get_path_name(), only_if_is_dirty=False)
print("PVT", P)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=32, yaw=40))
