import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "SkyAtmosphere":
        a.set_actor_location(unreal.Vector(0, 0, -100000.0), False, False); print("ATMO z=-100000")
