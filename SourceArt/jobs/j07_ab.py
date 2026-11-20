import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "HeavenClouds":
        c = a.get_component_by_class(unreal.VolumetricCloudComponent)
        c.set_visibility(not c.is_visible())
        print("AB cloud visible now", c.is_visible())
