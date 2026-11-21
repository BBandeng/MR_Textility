HLSL = 'float3 p = Pos;\nfloat off = (1.0 - saturate(Conv)) * 2600.0;\nfloat shape = 0.0;\nfloat3 c; float3 e; float d;\nc = float3(-1562.9 + -1.0*off, 1218.2 + 0.0*off, 1697.1); e = float3(1099.1, 1271.1, 972.0); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(-1583.5 + -1.0*off, -1211.0 + 0.0*off, 1744.8); e = float3(1017.3, 1544.6, 985.6); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(174.5 + 0.0*off, -1829.1 + -1.0*off, 1782.6); e = float3(1293.1, 984.1, 904.6); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(1801.9 + 1.0*off, -1035.8 + 0.0*off, 1746.3); e = float3(1153.3, 1221.1, 973.3); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(1090.2 + 0.0*off, 1449.1 + 1.0*off, 1786.9); e = float3(1744.7, 1315.1, 918.7); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(1063.4 + 0.0*off, -3494.1 + -1.0*off, 174.7); e = float3(2883.5, 1746.6, 1952.7); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(3483.4 + 1.0*off, 201.7 + 0.0*off, 153.6); e = float3(1935.9, 3649.8, 1975.6); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(1132.1 + 0.0*off, 3917.3 + 1.0*off, -54.6); e = float3(2431.5, 2211.3, 1875.3); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(-1885.2 + 0.0*off, 3752.7 + 1.0*off, -173.4); e = float3(2996.2, 2287.0, 1995.4); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\nc = float3(-3576.1 + -1.0*off, -1402.6 + 0.0*off, 39.9); e = float3(2408.6, 3302.9, 1867.4); d = length((p - c) / e); shape = max(shape, saturate((1.0 - d) / Soft));\n{ float a = radians(-35.0); float3 q = p; q.xy = float2(q.x*cos(a) - q.y*sin(a), q.x*sin(a) + q.y*cos(a)); c = float3(9.5, 42.2, 0.0); e = float3(2766.0*0.13, 2105.0*0.17, 2056.0*0.06); d = length((q - c) / e); shape = max(shape, saturate((1.0 - d) / Soft) * FootAmt); }\nfloat3 uvw = (p + float3(Wind, Wind*0.6, 0.0) * T) / (Tile * 100.0);\nfloat n1 = Tex.SampleLevel(TexSampler, uvw, 0).r;\nfloat n2 = Tex.SampleLevel(TexSampler, uvw * 2.7 + 0.37, 0).r;\nfloat n = n1 * 0.7 + n2 * 0.3;\nfloat er = (1.0 - n) * NStr;\nfloat v = saturate((shape - er) / max(1.0 - er, 0.001));\nreturn v * Dens;'

import unreal
O=[]
LOG=r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt'
try:
    MEL=unreal.MaterialEditingLibrary
    EAL=unreal.EditorAssetLibrary
    AT=unreal.AssetToolsHelpers.get_asset_tools()
    D='/Game/Level1Heaven/Clouds'
    # 1. MPC
    MPCP=D+'/MPC_HeavenCanopy'
    if EAL.does_asset_exist(MPCP):
        mpc=unreal.load_asset(MPCP)
    else:
        mpc=AT.create_asset('MPC_HeavenCanopy',D,unreal.MaterialParameterCollection,unreal.MaterialParameterCollectionFactoryNew())
    sp=unreal.CollectionScalarParameter()
    sp.set_editor_property('parameter_name','CanopyConverge')
    sp.set_editor_property('default_value',1.0)
    mpc.set_editor_property('scalar_parameters',[sp])
    EAL.save_loaded_asset(mpc)
    O.append('mpc ok')
    # 2. material copy
    MP=D+'/M_HeavenCanopyRing'
    if EAL.does_asset_exist(MP):
        raise Exception('material already exists: '+MP)
    m=EAL.duplicate_asset('/Game/StylizedVolClouds/Materials/M_StylizedVolumetricClouds',MP)
    X=-1200; Y=1400
    cu=MEL.create_material_expression(m,unreal.MaterialExpressionCustom,X,Y)
    cu.set_editor_property('code',HLSL)
    cu.set_editor_property('output_type',unreal.CustomMaterialOutputType.CMOT_FLOAT1)
    cu.set_editor_property('description','HeavenCanopyDensity')
    names=['Pos','Tex','T','Conv','Dens','Tile','NStr','Soft','Wind','FootAmt']
    ins=[]
    for n in names:
        ci=unreal.CustomInput()
        ci.set_editor_property('input_name',n)
        ins.append(ci)
    cu.set_editor_property('inputs',ins)
    wp=MEL.create_material_expression(m,unreal.MaterialExpressionWorldPosition,X-500,Y)
    to=MEL.create_material_expression(m,unreal.MaterialExpressionTextureObject,X-500,Y+100)
    to.set_editor_property('texture',unreal.load_asset('/Game/StylizedVolClouds/Textures/VolumeTextures/VT_Voronoi'))
    tm=MEL.create_material_expression(m,unreal.MaterialExpressionTime,X-500,Y+250)
    cp=MEL.create_material_expression(m,unreal.MaterialExpressionCollectionParameter,X-500,Y+350)
    cp.set_editor_property('collection',mpc)
    cp.set_editor_property('parameter_name','CanopyConverge')
    MEL.connect_material_expressions(wp,'',cu,'Pos')
    MEL.connect_material_expressions(to,'',cu,'Tex')
    MEL.connect_material_expressions(tm,'',cu,'T')
    MEL.connect_material_expressions(cp,'',cu,'Conv')
    defs=[('Dens','Canopy Density',0.08),('Tile','Canopy Noise Tiling (m)',40.0),('NStr','Canopy Noise Erosion',0.9),('Soft','Canopy Edge Softness',0.35),('Wind','Canopy Wind Speed',150.0),('FootAmt','Canopy Foot Amount',1.0)]
    yy=Y+450
    for pin,pname,val in defs:
        s=MEL.create_material_expression(m,unreal.MaterialExpressionScalarParameter,X-500,yy); yy+=90
        s.set_editor_property('parameter_name',pname)
        s.set_editor_property('default_value',val)
        s.set_editor_property('group','Canopy')
        MEL.connect_material_expressions(s,'',cu,pin)
    O.append('connect prop='+str(MEL.connect_material_property(cu,'',unreal.MaterialProperty.MP_SUBSURFACE_COLOR)))
    MEL.recompile_material(m)
    EAL.save_loaded_asset(m)
    O.append('mat ok')
    # 3. MI
    MIP=D+'/MI_HeavenCanopyVolClouds'
    if EAL.does_asset_exist(MIP):
        mi=unreal.load_asset(MIP)
    else:
        mi=AT.create_asset('MI_HeavenCanopyVolClouds',D,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
    mi.set_editor_property('parent',m)
    MEL.set_material_instance_vector_parameter_value(mi,'Cloud Color',unreal.LinearColor(1.0,0.96,0.9,1.0))
    for k,v in [('PhaseG',0.856),('PhaseG2',0.168),('PhaseBlend',0.232),('MultiScatteringContribution',1.0),('MultiScatteringOcclusion',1.0),('MultiScatteringEccentricity',1.0)]:
        MEL.set_material_instance_scalar_parameter_value(mi,k,v)
    MEL.update_material_instance(mi)
    EAL.save_loaded_asset(mi)
    O.append('mi ok')
    # 4. cloud actor
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    va=[a for a in es.get_all_level_actors() if isinstance(a,unreal.VolumetricCloud)][0]
    v=va.get_component_by_class(unreal.VolumetricCloudComponent)
    with unreal.ScopedEditorTransaction('Canopy ring volumetric clouds'):
        va.modify(); v.modify()
        v.set_editor_property('material',mi)
        v.set_editor_property('layer_bottom_altitude',0.028)
        v.set_editor_property('layer_height',0.07)
        v.set_editor_property('tracing_max_distance',3.0)
        v.set_editor_property('view_sample_count_scale',4.0)
        v.set_visibility(True,True)
        va.set_actor_label('VolumetricCloud_CanopyRing')
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for c in ['r.VolumetricCloud.DistanceToSampleMaxCount 0.4','r.VolumetricCloud.ViewRaySampleMaxCount 256']:
        unreal.SystemLibrary.execute_console_command(w,c)
    O.append('actor ok '+va.get_actor_label()+' vis='+str(v.is_visible()))
except Exception as e:
    import traceback
    O.append('ERR '+traceback.format_exc())
open(LOG,'w',encoding='utf-8').write(chr(10).join(O))
