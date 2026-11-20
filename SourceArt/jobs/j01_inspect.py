import unreal, json, traceback

OUT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/inspect_report.json"
rep = {}

def safe(fn):
    try:
        return fn()
    except Exception as e:
        return "ERR: " + repr(e)

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
rep["world"] = world.get_path_name()

actors = []
for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
    d = {"label": a.get_actor_label(), "class": a.get_class().get_name(),
         "loc": [round(v, 1) for v in (a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z)],
         "scale": [round(v, 2) for v in (a.get_actor_scale3d().x, a.get_actor_scale3d().y, a.get_actor_scale3d().z)]}
    comps = []
    for c in a.get_components_by_class(unreal.ActorComponent):
        cd = {"name": c.get_name(), "class": c.get_class().get_name()}
        if isinstance(c, unreal.StaticMeshComponent) and c.static_mesh:
            cd["mesh"] = c.static_mesh.get_path_name()
            cd["mats"] = [safe(lambda i=i: c.get_material(i).get_path_name()) for i in range(c.get_num_materials())]
        if isinstance(c, unreal.LightComponent):
            cd["intensity"] = safe(lambda: c.intensity)
            cd["atmo_sun"] = safe(lambda: c.get_editor_property("atmosphere_sun_light"))
        if isinstance(c, unreal.PostProcessComponent):
            cd["unbound"] = safe(lambda: c.unbound)
            cd["blendables"] = safe(lambda: str(c.settings.weighted_blendables.array))
        comps.append(cd)
    d["comps"] = comps
    o, e = a.get_actor_bounds(False)
    d["bounds_org"] = [round(o.x), round(o.y), round(o.z)]
    d["bounds_ext"] = [round(e.x), round(e.y), round(e.z)]
    actors.append(d)
rep["actors"] = actors

def mat_info(path):
    m = unreal.load_asset(path)
    if m is None:
        return None
    info = {"class": m.get_class().get_name()}
    base = m if isinstance(m, unreal.Material) else safe(lambda: m.get_base_material())
    if isinstance(base, unreal.Material):
        info["domain"] = str(base.get_editor_property("material_domain"))
        info["blend"] = str(base.get_editor_property("blend_mode"))
        info["shading"] = str(base.get_editor_property("shading_model"))
        info["base"] = base.get_path_name()
    ml = unreal.MaterialEditingLibrary
    info["scalars"] = [str(n) for n in safe(lambda: ml.get_scalar_parameter_names(m)) or []]
    info["vectors"] = [str(n) for n in safe(lambda: ml.get_vector_parameter_names(m)) or []]
    info["textures"] = [str(n) for n in safe(lambda: ml.get_texture_parameter_names(m)) or []]
    if isinstance(m, unreal.MaterialInstance):
        info["scalar_vals"] = {str(n): safe(lambda n=n: ml.get_material_instance_scalar_parameter_value(m, n)) for n in info["scalars"]}
    return info

mats = {}
for p in ["/Game/GoldenSky/M_OilPaint", "/Game/GoldenSky/M_SkyPainting", "/Game/GoldenSky/M_Sky_Test2",
          "/Game/GoldenSky/M_Sky_Test3", "/Game/GoldenSky/M_GodRay", "/Game/GoldenSky/M_SunCore",
          "/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud",
          "/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst"]:
    mats[p] = safe(lambda p=p: mat_info(p))
rep["materials"] = mats

rep["engine_cloud_assets"] = safe(lambda: [str(x) for x in unreal.EditorAssetLibrary.list_assets("/Engine/EngineSky/VolumetricClouds", recursive=True)])

bp_path = "/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter"
def bp_info():
    bp = unreal.load_asset(bp_path)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    hs = sds.k2_gather_subobject_data_for_blueprint(bp)
    out = []
    for h in hs:
        data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
        obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
        out.append([str(unreal.SubobjectDataBlueprintFunctionLibrary.get_variable_name(data)), obj.get_class().get_name() if obj else None])
    cdo = unreal.get_default_object(bp.generated_class())
    return {"subobjects": out, "capsule_half_height": safe(lambda: cdo.capsule_component.get_unscaled_capsule_half_height())}
rep["player_bp"] = safe(bp_info)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
print("INSPECT_DONE", OUT)
