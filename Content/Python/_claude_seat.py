import unreal
O=[]
try:
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    A={a.get_actor_label():a for a in es.get_all_level_actors()}
    with unreal.ScopedEditorTransaction('Seated eye height: lower floor and PlayerStart 50cm'):
        for n in ['DomeFloor_Collision','PlayerStart']:
            a=A[n]; a.modify()
            l=a.get_actor_location()
            a.set_actor_location(unreal.Vector(l.x,l.y,l.z-50.0),False,False)
            O.append(n+' z '+str(l.z)+' -> '+str(a.get_actor_location().z))
    f=A['DomeFloor_Collision']
    O.append('floor hiddenInGame='+str(f.get_editor_property('hidden'))+' coll='+str(f.static_mesh_component.get_collision_enabled()))
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
open(r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt','w',encoding='utf-8').write(chr(10).join(O))
