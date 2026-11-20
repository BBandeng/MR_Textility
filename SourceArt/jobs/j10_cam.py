import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=25, yaw=0))
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if c.static_mesh and ("Canopy" in c.static_mesh.get_name() or "Sky" in c.static_mesh.get_name()):
            print("CAM", a.get_actor_label(), c.is_visible(), a.is_hidden_ed(), a.is_temporarily_hidden_in_editor(), [c.get_material(i).get_name() for i in range(c.get_num_materials())])
