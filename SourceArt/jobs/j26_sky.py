import unreal
MEL = unreal.MaterialEditingLibrary
m = unreal.load_asset("/Game/Layer1/Materials/M_Sky_LowerDome")
m.set_editor_property("is_sky", False)
MEL.recompile_material(m)
unreal.EditorAssetLibrary.save_asset(m.get_path_name(), only_if_is_dirty=False)
src = unreal.load_asset("/Game/GoldenSky/M_Sky_Test2")
print("SKY src is_sky", src.get_editor_property("is_sky"), "two_sided", src.get_editor_property("two_sided"))
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "CloudWorld":
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if c.get_name().startswith("SunDome"):
                print("SKY comp", c.get_name(), c.is_visible(), c.get_world_location(), c.get_world_scale(), [x.get_name() for x in c.get_materials()])
