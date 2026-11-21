HLSL = '\nfloat3 p = Pos;\nfloat off = (1.0 - saturate(Conv)) * 2600.0;\n// low-frequency domain warp -> irregular outlines\nfloat3 wuv = (p + float3(Wind*0.3, Wind*0.2, 0.0) * T) / (Tile * 300.0);\nfloat3 w3 = Tex.SampleLevel(TexSampler, wuv, 0).rgb - 0.5;\nfloat3 pw = p + w3 * Var * 900.0;\nconst float3 C1[5] = { float3(-1563.0,1218.0,1697.0), float3(-1583.0,-1211.0,1745.0), float3(174.0,-1829.0,1783.0), float3(1802.0,-1036.0,1746.0), float3(1090.0,1449.0,1787.0) };\nconst float3 E1[5] = { float3(1293.0,1495.0,1215.0), float3(1197.0,1817.0,1232.0), float3(1521.0,1158.0,1131.0), float3(1357.0,1437.0,1217.0), float3(2053.0,1547.0,1148.0) };\nconst float2 D1[5] = { float2(-1.0,0.0), float2(-1.0,0.0), float2(0.0,-1.0), float2(1.0,0.0), float2(0.0,1.0) };\nconst float3 C2[5] = { float3(1063.0,-3494.0,175.0), float3(3483.0,202.0,154.0), float3(1132.0,3917.0,-55.0), float3(-1885.0,3753.0,-173.0), float3(-3576.0,-1403.0,40.0) };\nconst float3 E2[5] = { float3(3392.0,2055.0,2441.0), float3(2278.0,4294.0,2470.0), float3(2861.0,2602.0,2344.0), float3(3525.0,2691.0,2494.0), float3(2834.0,3886.0,2334.0) };\nconst float2 D2[5] = { float2(0.0,-1.0), float2(1.0,0.0), float2(0.0,1.0), float2(0.0,1.0), float2(-1.0,0.0) };\nfloat shape = 0.0;\nint nl = (int)clamp(Layers, 1.0, 3.0);\n// upper rings (original top ring + extra stacked rings)\nfor (int k = 0; k < 3; k++)\n{\n  if (k >= nl) break;\n  float ang = radians(36.0 * k + 18.0 * (k > 1 ? 1.0 : 0.0));\n  float ca = cos(ang); float sa = sin(ang);\n  float rs = Gather * pow(RScale, (float)k);\n  for (int i = 0; i < 5; i++)\n  {\n    float3 c = C1[i];\n    float2 xy = c.xy * rs;\n    xy = float2(xy.x*ca - xy.y*sa, xy.x*sa + xy.y*ca);\n    if (k == 0) xy += D1[i] * off; else xy += normalize(xy) * off;\n    c = float3(xy, c.z + LSpace * 100.0 * k);\n    float3 e = E1[i] * pow(0.88, (float)k);\n    float seed = i * 7.31 + k * 3.17 + 1.0;\n    for (int j = 0; j < 4; j++)\n    {\n      float h1 = frac(sin(seed * 12.9898 + j * 78.233) * 43758.5453);\n      float h2 = frac(sin(seed * 39.3468 + j * 11.135) * 24634.6345);\n      float h3 = frac(sin(seed * 73.1560 + j * 52.235) * 56445.2345);\n      float3 lo = (j == 0) ? float3(0,0,0) : float3(h1 - 0.5, h2 - 0.5, (h3 - 0.5) * 0.6) * 1.1;\n      float r = (j == 0) ? (0.75 + 0.2 * h3) : (0.35 + 0.35 * h1);\n      float3 st = float3(1.0 + 0.5 * (h2 - 0.5), 1.0 + 0.5 * (h1 - 0.5), 0.8 + 0.4 * h3);\n      float d = length(((pw - c) / e - lo) / (r * st));\n      shape = max(shape, saturate((1.0 - d) / Soft));\n    }\n  }\n}\n// lower ring (unchanged layout, also varied outline)\nfor (int i2 = 0; i2 < 5; i2++)\n{\n  float3 c = C2[i2];\n  c.xy += D2[i2] * off;\n  float3 e = E2[i2];\n  float seed = i2 * 5.17 + 40.0;\n  for (int j = 0; j < 4; j++)\n  {\n    float h1 = frac(sin(seed * 12.9898 + j * 78.233) * 43758.5453);\n    float h2 = frac(sin(seed * 39.3468 + j * 11.135) * 24634.6345);\n    float h3 = frac(sin(seed * 73.1560 + j * 52.235) * 56445.2345);\n    float3 lo = (j == 0) ? float3(0,0,0) : float3(h1 - 0.5, h2 - 0.5, (h3 - 0.5) * 0.6) * 1.1;\n    float r = (j == 0) ? (0.75 + 0.2 * h3) : (0.35 + 0.35 * h1);\n    float d = length(((pw - c) / e - lo) / r);\n    shape = max(shape, saturate((1.0 - d) / Soft));\n  }\n}\n// foot cloud\n{ float a = radians(-35.0); float3 q = pw; q.xy = float2(q.x*cos(a) - q.y*sin(a), q.x*sin(a) + q.y*cos(a));\n  float d = length((q - float3(9.5, 42.2, 0.0)) / float3(359.6, 357.9, 123.4));\n  shape = max(shape, saturate((1.0 - d) / Soft) * FootAmt); }\nfloat3 uvw = (p + float3(Wind, Wind*0.6, 0.0) * T) / (Tile * 100.0);\nfloat n1 = Tex.SampleLevel(TexSampler, uvw, 0).r;\nfloat n2 = Tex.SampleLevel(TexSampler, uvw * 2.7 + 0.37, 0).r;\nfloat n = n1 * 0.7 + n2 * 0.3;\nfloat er = (1.0 - n) * NStr;\nfloat v = saturate((shape - er) / max(1.0 - er, 0.001));\nreturn v * Dens;\n'
import unreal
O=[]
try:
    L=unreal.MaterialEditingLibrary
    m=unreal.load_asset('/Game/Level1Heaven/Clouds/M_HeavenCanopyRing')
    cu=L.get_material_property_input_node(m,unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
    ins=list(cu.get_editor_property('inputs'))
    have=[str(i.get_editor_property('input_name')) for i in ins]
    O.append('have='+str(have))
    new=[('Gather','Canopy Top Gather',0.75),('LSpace','Canopy Layer Spacing (m)',11.0),('RScale','Canopy Upper Layer Radius Scale',0.82),('Var','Canopy Outline Variation',1.0),('Layers','Canopy Top Layers',3.0)]
    for pin,pn,dv in new:
        if pin not in have:
            ci=unreal.CustomInput(); ci.set_editor_property('input_name',pin); ins.append(ci)
    cu.set_editor_property('inputs',ins)
    cu.set_editor_property('code',HLSL)
    y=3000
    for pin,pn,dv in new:
        if pin in have: continue
        s=L.create_material_expression(m,unreal.MaterialExpressionScalarParameter,-1700,y); y+=90
        s.set_editor_property('parameter_name',pn); s.set_editor_property('default_value',dv); s.set_editor_property('group','Canopy')
        L.connect_material_expressions(s,'',cu,pin)
    L.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m)
    O.append('stats='+str(L.get_statistics(m).num_pixel_shader_instructions))
    es=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    va=[a for a in es.get_all_level_actors() if isinstance(a,unreal.VolumetricCloud)][0]
    v=va.get_component_by_class(unreal.VolumetricCloudComponent)
    with unreal.ScopedEditorTransaction('Taller canopy cloud layer'):
        va.modify(); v.modify()
        v.set_editor_property('layer_bottom_altitude',0.0)
        v.set_editor_property('layer_height',0.135)
    O.append('ok')
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
open(r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt','w',encoding='utf-8').write(chr(10).join(O))
