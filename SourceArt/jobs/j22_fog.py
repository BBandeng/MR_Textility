import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "ExponentialHeightFog":
        c = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
        print("FOG before", a.get_actor_location(), c.get_editor_property("fog_density"), c.get_editor_property("fog_height_falloff"))
        l = a.get_actor_location()
        a.set_actor_location(unreal.Vector(l.x, l.y, -60000.0), False, False)
        print("FOG moved to z=-60000")
