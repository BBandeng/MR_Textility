import unreal
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
m = unreal.load_asset("/Game/HeavenClouds/M_HeavenCloudVolume")
print("FLAG candidates", [n for n in dir(m) if "cloud" in n.lower() or "used_with" in n.lower()][:60])
ok = False
for name in ["used_with_volumetric_cloud", "b_used_with_volumetric_cloud"]:
    try:
        m.set_editor_property(name, True); ok = True; print("FLAG set", name); break
    except Exception as e:
        print("FLAG fail", name, repr(e))
if not ok:
    try:
        r = MEL.set_material_usage(m, unreal.MaterialUsage.MATUSAGE_VOLUMETRIC_CLOUD)
        print("FLAG via usage", r)
    except Exception as e:
        print("FLAG usage fail", repr(e), [n for n in dir(unreal.MaterialUsage) if "CLOUD" in n.upper()])
MEL.recompile_material(m)
EAL.save_asset("/Game/HeavenClouds/M_HeavenCloudVolume", only_if_is_dirty=False)
print("FLAG done")
