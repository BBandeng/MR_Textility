import unreal
MEL = unreal.MaterialEditingLibrary
mi = unreal.load_asset("/Game/PaintClouds/MI_VolCloud")
SCALE, COVER, DENS, BOTTOM, HEIGHT, PITCH = 60.0, -0.05, 0.03, 2.2, 2.0, 20
MEL.set_material_instance_scalar_parameter_value(mi, "Layout_CloudGlobalScale", SCALE)
MEL.set_material_instance_scalar_parameter_value(mi, "Cloud_GlobalCoverage", COVER)
MEL.set_material_instance_scalar_parameter_value(mi, "Cloud_GlobalDensity", DENS)
MEL.update_material_instance(mi); unreal.EditorAssetLibrary.save_asset(mi.get_path_name(), only_if_is_dirty=False)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "VolumetricCloud":
        c = a.get_component_by_class(unreal.VolumetricCloudComponent)
        c.set_editor_property("layer_bottom_altitude", BOTTOM); c.set_editor_property("layer_height", HEIGHT)
        c.set_editor_property("material", mi)
        print("VT", c.is_visible(), c.get_editor_property("tracing_max_distance"), c.get_editor_property("tracing_start_max_distance"))
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=PITCH, yaw=0))
print("VT done")
