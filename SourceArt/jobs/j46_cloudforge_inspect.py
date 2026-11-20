import unreal, os, shutil, json
SRC = "C:/Users/Bartl/Desktop/5.3/Cloud_Forge_VDB_Vol3"
DST = "C:/Users/Bartl/Desktop/MRPARADISE/Content/Cloud_Forge_VDB_Vol3"
rep = {}
if not os.path.exists(DST):
    shutil.copytree(SRC, DST); rep["copied"] = True
ar = unreal.AssetRegistryHelpers.get_asset_registry()
ar.scan_paths_synchronous(["/Game/Cloud_Forge_VDB_Vol3"], True)
EAL = unreal.EditorAssetLibrary
assets = EAL.list_assets("/Game/Cloud_Forge_VDB_Vol3", recursive=True)
rep["count"] = len(assets)
def info(path):
    try:
        a = unreal.load_asset(path)
        return a.get_class().get_name() if a else None
    except Exception as e:
        return "ERR " + repr(e)
rep["kit"] = info("/Game/Cloud_Forge_VDB_Vol3/VDB_Collection/VDB_AP_Cumulus_Cloud/Kit_cumulus_04")
base = set(dir(unreal.Actor))
for n in ["BP_Cloud_Forge_Single_Cloud", "BP_Cloud_Forge_Multi_Cloud", "BP_Volumetric_VDB"]:
    try:
        bp = unreal.load_asset(f"/Game/Cloud_Forge_VDB_Vol3/Blueprint/{n}")
        cdo = unreal.get_default_object(bp.generated_class())
        props = [p for p in dir(cdo) if p not in base and not p.startswith("_")]
        vals = {}
        for p in props:
            try: vals[p] = str(cdo.get_editor_property(p))[:160]
            except Exception: pass
        sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); SDL = unreal.SubobjectDataBlueprintFunctionLibrary
        comps = []
        for h in sds.k2_gather_subobject_data_for_blueprint(bp):
            o = SDL.get_object(SDL.get_data(h))
            if o: comps.append([o.get_name(), o.get_class().get_name()])
        rep[n] = {"props": vals, "comps": comps}
    except Exception as e:
        rep[n] = "ERR " + repr(e)
MEL = unreal.MaterialEditingLibrary
rep["mel_sparse"] = [f for f in dir(MEL) if "sparse" in f.lower() or "volume" in f.lower()]
for mn in ["VDB_Single_Material/MI_VDB_Cloud_Single", "VDB_Multi_Cloud_Material/MI_VDB_Cloud_Multi_01"]:
    try:
        mi = unreal.load_asset(f"/Game/Cloud_Forge_VDB_Vol3/VDB_Materials/{mn}")
        d = {"scalars": {str(n): MEL.get_material_instance_scalar_parameter_value(mi, n) for n in MEL.get_scalar_parameter_names(mi)},
             "vectors": [str(n) for n in MEL.get_vector_parameter_names(mi)], "textures": [str(n) for n in MEL.get_texture_parameter_names(mi)]}
        for f in rep["mel_sparse"]:
            if f.startswith("get_") and "names" in f:
                try: d[f] = [str(x) for x in getattr(MEL, f)(mi)]
                except Exception as e: d[f] = repr(e)
        rep[mn] = d
    except Exception as e:
        rep[mn] = "ERR " + repr(e)
rep["hv_props"] = [p for p in dir(unreal.HeterogeneousVolumeComponent) if not p.startswith("_") and p not in set(dir(unreal.MeshComponent))]
json.dump(rep, open("C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/inspect_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("CF INSPECT DONE")
