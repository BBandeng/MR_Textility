import unreal
LOG=r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt'
les=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not les.is_in_play_in_editor():
    les.editor_play_simulate() if False else les.editor_request_begin_play()
    open(LOG,'w').write('started')
else:
    O=[]
    try:
        gw=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        cm=unreal.GameplayStatics.get_player_camera_manager(gw,0)
        O.append('camloc='+str(cm.get_camera_location()))
        pw=unreal.GameplayStatics.get_player_pawn(gw,0)
        O.append('pawn='+str(pw.get_actor_location() if pw else None))
        for a in unreal.GameplayStatics.get_all_actors_of_class(gw,unreal.StaticMeshActor):
            if False:
                O.append('floor hidden='+str(a.is_hidden()))
    except Exception as e:
        import traceback; O.append('ERR '+traceback.format_exc())
    les.editor_request_end_play()
    open(LOG,'w').write(chr(10).join(O))
