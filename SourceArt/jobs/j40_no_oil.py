import unreal
bp = unreal.load_asset("/Game/Layer1/Blueprints/BP_CloudWorld")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); SDL = unreal.SubobjectDataBlueprintFunctionLibrary
n = 0
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o = SDL.get_object(SDL.get_data(h))
    if isinstance(o, unreal.PostProcessComponent):
        o.set_editor_property("enabled", False); o.set_editor_property("blend_weight", 0.0); n += 1
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
unreal.EditorAssetLibrary.save_asset(bp.get_path_name(), only_if_is_dirty=False)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "CloudWorld":
        for c in a.get_components_by_class(unreal.PostProcessComponent):
            c.set_editor_property("enabled", False); c.set_editor_property("blend_weight", 0.0)
            print("NOOIL instance", c.get_editor_property("enabled"))
print("NOOIL templates", n)
