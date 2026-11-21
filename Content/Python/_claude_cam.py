import unreal
O=[]
def g(o,p):
    try: return o.get_editor_property(p)
    except Exception as e: return '?'
try:
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    ws=w.get_world_settings()
    gm=g(ws,'default_game_mode')
    O.append('ws gamemode override='+str(gm))
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in es.get_all_level_actors():
        cn=a.get_class().get_name()
        if any(k in cn for k in ['PlayerStart','Camera','Pawn','Character','Sequence','XR','VR','Origin']):
            O.append('ACT '+a.get_actor_label()+' cls='+a.get_class().get_path_name()+' loc='+str(a.get_actor_location())+' rot='+str(a.get_actor_rotation()))
    # project default game mode
    gms=unreal.GameMapsSettings.get_game_maps_settings() if hasattr(unreal.GameMapsSettings,'get_game_maps_settings') else None
    O.append('gms='+str(gms))
    if gms:
        for p in ['global_default_game_mode','game_default_map','editor_startup_map']:
            O.append(p+'='+str(g(gms,p)))
    gmc=gm if gm and gm!='?' else None
    if not gmc and gms:
        gmc=g(gms,'global_default_game_mode')
    O.append('gm class='+str(gmc))
    if gmc and gmc!='?':
        try:
            cls=unreal.load_class(None,str(gmc)) if isinstance(gmc,(str,unreal.SoftClassPath)) else gmc
        except Exception as e:
            cls=None; O.append('loadcls err '+repr(e))
        if cls:
            cdo=unreal.get_default_object(cls)
            pawn=g(cdo,'default_pawn_class'); O.append('default pawn='+str(pawn))
            if pawn and pawn!='?':
                pc=unreal.get_default_object(pawn)
                O.append('pawn cdo='+str(pc)+' base_eye='+str(g(pc,'base_eye_height')))
                # components via SubobjectDataSubsystem
                bp_path=pawn.get_path_name().replace('_C','') if hasattr(pawn,'get_path_name') else ''
                O.append('bp='+bp_path)
                try:
                    bp=unreal.load_asset(bp_path.split('.')[0])
                    sds=unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
                    hs=sds.k2_gather_subobject_data_for_blueprint(bp)
                    for h in hs:
                        d=unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
                        ob=unreal.SubobjectDataBlueprintFunctionLibrary.get_object(d)
                        if ob is None: continue
                        s=ob.get_class().get_name()+' '+ob.get_name()
                        if isinstance(ob,unreal.SceneComponent):
                            s+=' rel='+str(ob.get_editor_property('relative_location'))
                        if isinstance(ob,unreal.CapsuleComponent):
                            s+=' halfh='+str(ob.get_editor_property('capsule_half_height'))
                        O.append('  COMP '+s)
                except Exception as e: O.append('bp err '+repr(e))
    s=unreal.load_asset('/Game/Level1Heaven/LS_Level1Heaven_RealClouds')
    O.append('camcuts='+str([t.get_class().get_name() for t in s.get_tracks()]))
    for b in s.get_spawnables() if hasattr(s,'get_spawnables') else []:
        O.append('spawnable '+str(b.get_display_name()))
    xr=[p for p in ['OpenXR','OculusVR','SteamVR','XRBase','AppleARKit','MetaXR'] if unreal.SystemLibrary.get_console_variable_int_value('vr.HMDVersion')>=0]
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
open(r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt','w',encoding='utf-8').write(chr(10).join(O))
