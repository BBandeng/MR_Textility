import unreal
O=[]
try:
    gms=unreal.GameMapsSettings.get_game_maps_settings()
    gmp=gms.get_editor_property('global_default_game_mode').export_text()
    O.append('gm='+gmp)
    cls=unreal.load_class(None,gmp)
    cdo=unreal.get_default_object(cls)
    pawn=cdo.get_editor_property('default_pawn_class')
    O.append('pawn='+pawn.get_path_name())
    pc=unreal.get_default_object(pawn)
    for p in ['base_eye_height','crouched_eye_height']:
        try: O.append(p+'='+str(pc.get_editor_property(p)))
        except Exception: pass
    bp=unreal.load_asset(pawn.get_path_name().rsplit('.',1)[0])
    O.append('bp='+str(bp))
    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    for h in sds.k2_gather_subobject_data_for_blueprint(bp):
        d=unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
        ob=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
        if ob is None: continue
        s=ob.get_class().get_name()+' '+ob.get_name()
        if isinstance(ob,unreal.SceneComponent):
            s+=' rel='+str(ob.get_editor_property('relative_location'))
            try:
                par=ob.get_attach_parent(); s+=' par='+(par.get_name() if par else '')
            except Exception: pass
        if isinstance(ob,unreal.CapsuleComponent):
            s+=' halfh='+str(ob.get_editor_property('capsule_half_height'))
        if isinstance(ob,unreal.CameraComponent):
            s+=' pawnctrl='+str(ob.get_editor_property('use_pawn_control_rotation'))+' lockhmd='+str(ob.get_editor_property('lock_to_hmd'))
        O.append('  COMP '+s)
    # who else uses this pawn / game mode
    ar=unreal.AssetRegistryHelpers.get_asset_registry()
    O.append('pawn referencers='+str([str(x) for x in unreal.EditorAssetLibrary.find_package_referencers_for_asset(pawn.get_path_name().rsplit('.',1)[0])]))
    O.append('xr='+str(unreal.HeadMountedDisplayFunctionLibrary.is_head_mounted_display_enabled())+' '+str(unreal.HeadMountedDisplayFunctionLibrary.get_hmd_device_name()))
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
open(r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt','w',encoding='utf-8').write(chr(10).join(O))
