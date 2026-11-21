import unreal, random
O=[]
LOG=r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log2.txt'
try:
    random.seed(7)
    MAP={'de1e1499':'Angel1','d728b0bc':'Angel2','2f742d84':'Angel3','d17daee8':'Angel4','Dove_04':'Dove1','Dove_03':'Dove2','Dove_01':'Dove3'}
    base='/Game/Level1Heaven/Animated/'
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    targets=[]
    for a in es.get_all_level_actors():
        if not isinstance(a,unreal.StaticMeshActor): continue
        l=a.get_actor_label()
        for k,v in MAP.items():
            if k in l: targets.append((a,v))
    existing={x.get_actor_label() for x in es.get_all_level_actors()}
    with unreal.ScopedEditorTransaction('Animated angels/doves replace static meshes'):
        for a,n in targets:
            lab=a.get_actor_label()+'_Anim'
            if lab in existing:
                O.append('skip exists '+lab); continue
            sk=unreal.load_asset(base+n+'/'+n+'/SkeletalMeshes/'+n)
            an=unreal.load_asset(base+n+'/'+n+'/SkeletalMeshes/'+n+'_Anim')
            ska=es.spawn_actor_from_class(unreal.SkeletalMeshActor,a.get_actor_location(),a.get_actor_rotation())
            ska.set_actor_label(lab)
            ska.attach_to_actor(a,'',unreal.AttachmentRule.SNAP_TO_TARGET,unreal.AttachmentRule.SNAP_TO_TARGET,unreal.AttachmentRule.SNAP_TO_TARGET,False)
            c=ska.skeletal_mesh_component
            c.set_skinned_asset_and_update(sk) if hasattr(c,'set_skinned_asset_and_update') else c.set_editor_property('skeletal_mesh_asset',sk)
            c.set_editor_property('animation_mode',unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            pd=unreal.SingleAnimationPlayData()
            pd.set_editor_property('anim_to_play',an)
            pd.set_editor_property('saved_looping',True)
            pd.set_editor_property('saved_playing',True)
            pd.set_editor_property('saved_position',random.uniform(0.0,an.get_play_length()))
            pd.set_editor_property('saved_play_rate',random.uniform(0.9,1.1))
            c.set_editor_property('animation_data',pd)
            try: c.set_editor_property('update_animation_in_editor',True)
            except Exception: pass
            # hide the old static mesh but keep the actor (it carries the sequence animation)
            a.modify()
            smc=a.static_mesh_component
            smc.modify()
            smc.set_visibility(False,False)
            smc.set_editor_property('hidden_in_game',True)
            rel=ska.root_component.get_editor_property('relative_location')
            O.append('OK '+lab+' -> '+n+' rel='+str(rel)+' scale='+str(ska.get_actor_scale3d()))
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
open(LOG,'w',encoding='utf-8').write(chr(10).join(O).replace('<Struct ','<'))
