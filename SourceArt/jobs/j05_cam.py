import unreal
ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(0, -600, 170), unreal.Rotator(roll=0, pitch=-8, yaw=90))
print("CAM set")
