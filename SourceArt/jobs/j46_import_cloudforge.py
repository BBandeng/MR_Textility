# Copies the Cloud Forge VDB pack from Desktop/5.3 into the project Content folder and inspects it.
import unreal, shutil, os, json
SRC = "C:/Users/Bartl/Desktop/5.3/Cloud_Forge_VDB_Vol3"
DST = "C:/Users/Bartl/Desktop/MRPARADISE/Content/Cloud_Forge_VDB_Vol3"
rep = {}
if not os.path.exists(DST):
    shutil.copytree(SRC, DST)
    rep["copied"] = True
ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.scan_paths_synchronous(["/Game/Cloud_Forge_VDB_Vol3"], True)
assets = ar.get_assets_by_path("/Game/Cloud_Forge_VDB_Vol3", recursive=True)
rep["assets"] = sorted([f"{a.package_name} [{a.asset_class_path.asset_name}]" for a in assets])
def safe(fn):
    try: return fn()
    except Exception as e: return "ERR " + repr(e)
info = {}
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); SDL = unreal.SubobjectDataBlueprintFunctionLibrary
for name in ["BP_Cloud_Forge_Single_Cloud", "BP_Cloud_Forge_Multi_Cloud", "BP_Volumetric_VDB"]:
    bp = safe(lambda: unreal.load_asset(f"/Game/Cloud_Forge_VDB_Vol3/Blueprint/{name}"))
    d = {"loaded": str(bp)}
    if isinstance(bp, unreal.Blueprint):
        comps = []
        for h in sds.k2_gather_subobject_data_for_blueprint(bp):
            data = SDL.get_data(h); o = SDL.get_object(data)
            c = {"var": str(SDL.get_variable_name(data)), "class": o.get_class().get_name() if o else None}
            if o and "Heterogeneous" in o.get_class().get_name():
                c["props"] = [p for p in dir(o) if not p.startswith("_") and any(k in p for k in ("material", "volume", "frame", "step", "shadow", "resolution", "lod", "scale"))][:60]
                c["materials"] = safe(lambda: [m.get_path_name() if m else None for m in o.get_editor_property("override_materials")])
                for p in ["volume_resolution", "step_factor", "shadow_step_factor", "lighting_downsample_factor"]:
                    c[p] = str(safe(lambda p=p: o.get_editor_property(p)))
            comps.append(c)
        d["components"] = comps
        cdo = unreal.get_default_object(bp.generated_class())
        base = set(dir(unreal.Actor))
        d["vars"] = {p: str(safe(lambda p=p: cdo.get_editor_property(p)))[:160] for p in dir(cdo) if p not in base and not p.startswith("_") and not callable(getattr(cdo, p, None))}
    info[name] = d
rep["blueprints"] = info
for mp in ["VDB_Materials/VDB_Single_Material/MI_VDB_Cloud_Single", "VDB_Materials/VDB_Single_Material/M_VDB_Cloud_Single"]:
    m = safe(lambda: unreal.load_asset("/Game/Cloud_Forge_VDB_Vol3/" + mp))
    if isinstance(m, unreal.MaterialInterface):
        ML = unreal.MaterialEditingLibrary
        rep[mp] = {"scalars": {str(n): safe(lambda n=n: ML.get_material_instance_scalar_parameter_value(m, n) if isinstance(m, unreal.MaterialInstanceConstant) else ML.get_material_default_scalar_parameter_value(m, n)) for n in ML.get_scalar_parameter_names(m)},
                   "vectors": [str(n) for n in ML.get_vector_parameter_names(m)], "textures": [str(n) for n in ML.get_texture_parameter_names(m)],
                   "class": m.get_class().get_name()}
    else: rep[mp] = str(m)
svt = safe(lambda: unreal.load_asset("/Game/Cloud_Forge_VDB_Vol3/VDB_Collection/VDB_AP_Cumulus_Cloud/Kit_cumulus_04"))
rep["svt"] = {"class": svt.get_class().get_name() if hasattr(svt, "get_class") else str(svt)}
rep["engine"] = unreal.SystemLibrary.get_engine_version()
json.dump(rep, open("C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/cloudforge_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("CF DONE")
