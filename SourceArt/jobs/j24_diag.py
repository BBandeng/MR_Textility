import unreal
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in EAS.get_all_level_actors():
    cls = a.get_class().get_name(); lab = a.get_actor_label()
    if lab == "CloudWorld":
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            c.set_visibility(c.get_name().startswith("Step") or c.get_name().startswith("SunDome"))
    if cls in ("ExponentialHeightFog", "SkyAtmosphere", "VolumetricCloud", "SkyLight", "DirectionalLight") or "Sky" in lab or lab == "Floor":
        info = [lab, cls, a.get_actor_location(), a.is_hidden_ed()]
        for c in a.get_components_by_class(unreal.SceneComponent):
            info.append((c.get_name(), c.is_visible()))
            if isinstance(c, unreal.ExponentialHeightFogComponent):
                for p in ["fog_density", "fog_height_falloff", "fog_max_opacity", "start_distance", "volumetric_fog", "fog_inscattering_luminance"]:
                    try: info.append((p, c.get_editor_property(p)))
                    except Exception as e: info.append((p, "?"))
            if isinstance(c, unreal.StaticMeshComponent):
                info.append(("scale", a.get_actor_scale3d(), c.static_mesh.get_bounding_box().min, c.static_mesh.get_bounding_box().max))
        print("DIAG", info)
