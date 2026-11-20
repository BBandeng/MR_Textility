import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "CloudWorld":
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            n = c.get_name()
            c.set_visibility(n.startswith("GoldenShell") or n.startswith("Step"))
        print("DIAG only shell+steps visible")
