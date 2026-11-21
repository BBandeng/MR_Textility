import unreal
O=[]
def bstr(b): return 'o=(%.1f,%.1f,%.1f) e=(%.1f,%.1f,%.1f)'%(b.origin.x,b.origin.y,b.origin.z,b.box_extent.x,b.box_extent.y,b.box_extent.z)
try:
    MAP={'de1e1499':'Angel1','d728b0bc':'Angel2','2f742d84':'Angel3','d17daee8':'Angel4','Dove_04':'Dove1','Dove_03':'Dove2','Dove_01':'Dove3'}
    sk={}
    for n in set(MAP.values()):
        for a in unreal.EditorAssetLibrary.list_assets('/Game/Level1Heaven/Animated/'+n,True,False):
            ad=unreal.EditorAssetLibrary.find_asset_data(a); c=str(ad.asset_class_path.asset_name)
            if c=='SkeletalMesh':
                m=unreal.load_asset(a); sk[n]=m
                O.append('SK '+n+' '+a+' '+bstr(m.get_bounds())+' imp='+bstr(m.get_imported_bounds()))
            if c=='AnimSequence':
                s=unreal.load_asset(a); O.append('  ANIM '+a+' len=%.2f'%s.get_play_length()+' skel='+str(s.get_editor_property('skeleton').get_path_name()))
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in es.get_all_level_actors():
        if not isinstance(a,unreal.StaticMeshActor): continue
        l=a.get_actor_label(); key=None
        for k in MAP:
            if k in l: key=k
        if not key: continue
        c=a.static_mesh_component; m=c.static_mesh
        p=a.get_attach_parent_actor()
        O.append('SM '+l+' -> '+MAP[key]+' mesh='+m.get_path_name()+' '+bstr(m.get_bounds())+' | loc='+str(a.get_actor_location())+' rot='+str(a.get_actor_rotation())+' scl='+str(a.get_actor_scale3d())+' comprel='+str(c.get_editor_property('relative_location'))+' par='+(p.get_actor_label() if p else '-')+' vis='+str(c.is_visible()))
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
open(r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log2.txt','w',encoding='utf-8').write(chr(10).join(O).replace('<Struct ','<'))
