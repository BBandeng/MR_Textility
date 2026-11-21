import unreal
O=[]
LOG=r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt'
try:
    EAL=unreal.EditorAssetLibrary
    NP='/Game/Level1Heaven/LS_Level1Heaven_RealClouds'
    if EAL.does_asset_exist(NP):
        raise Exception('sequence copy exists already')
    seq=EAL.duplicate_asset('/Game/LS_Level1Heaven',NP)
    # remove dead rig bindings
    for bd in list(seq.get_bindings()):
        n=str(bd.get_display_name())
        if n.startswith('Rig_Clouds'):
            bd.remove(); O.append('removed '+n)
    mpc=unreal.load_asset('/Game/Level1Heaven/Clouds/MPC_HeavenCanopy')
    tr=seq.add_track(unreal.MovieSceneMaterialParameterCollectionTrack)
    tr.set_editor_property('mpc',mpc)
    tr.set_display_name('Canopy Cloud Converge')
    sec=tr.add_section()
    sec.set_range(seq.get_playback_start(),seq.get_playback_end())
    tick=seq.get_tick_resolution(); disp=seq.get_display_rate()
    def tf(f):
        return unreal.FrameNumber(int(round(f*tick.numerator*disp.denominator/(tick.denominator*disp.numerator))))
    O.append('tick='+str(tick.numerator)+'/'+str(tick.denominator)+' disp='+str(disp.numerator))
    O.append('methods='+str([m for m in dir(sec) if 'scalar' in m.lower()]))
    sec.add_scalar_parameter_key('CanopyConverge',tf(0),0.0)
    sec.add_scalar_parameter_key('CanopyConverge',tf(90),0.0)
    sec.add_scalar_parameter_key('CanopyConverge',tf(270),1.0)
    EAL.save_loaded_asset(seq)
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in es.get_all_level_actors():
        if isinstance(a,unreal.LevelSequenceActor):
            with unreal.ScopedEditorTransaction('Use RealClouds sequence copy'):
                a.modify(); a.set_sequence(seq)
            O.append('actor '+a.get_actor_label()+' -> '+str(a.get_sequence()))
    O.append('ok')
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
open(LOG,'w',encoding='utf-8').write(chr(10).join(O))
