# Multi-layer volumetric clouds in the warm painted palette of the sky backdrop; hide gold-leaf shards.
import unreal
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
DEST = "/Game/PaintClouds"
errs = []
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: errs.append((n, repr(e)))

# ---- gold leaf off
bp = unreal.load_asset("/Game/Layer1/Blueprints/BP_CloudWorld")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); SDL = unreal.SubobjectDataBlueprintFunctionLibrary
def is_gold(c):
    try:
        ms = c.get_editor_property("override_materials")
        return bool(ms) and ms[0] is not None and ms[0].get_name() in ("MI_Shard_1", "MI_Shard_3")
    except Exception: return False
n = 0
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    o = SDL.get_object(SDL.get_data(h))
    if isinstance(o, unreal.StaticMeshComponent) and is_gold(o):
        setp(o, "visible", False); setp(o, "hidden_in_game", True); n += 1
unreal.BlueprintEditorLibrary.compile_blueprint(bp); EAL.save_asset(bp.get_path_name(), only_if_is_dirty=False)
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "CloudWorld":
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            if is_gold(c): c.set_visibility(False); c.set_hidden_in_game(True)
print("PV gold shards hidden", n)

# ---- volumetric material
MP = f"{DEST}/M_PaintVolCloud"
if EAL.does_asset_exist(MP):
    m = unreal.load_asset(MP); MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_PaintVolCloud", DEST, unreal.Material, unreal.MaterialFactoryNew())
setp(m, "material_domain", unreal.MaterialDomain.MD_VOLUME)
setp(m, "blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
setp(m, "used_with_volumetric_cloud", True)
PARAMS = [  # heights in metres (world Z, player's feet = 0)
    ("L1_Bottom", -1000.0), ("L1_Top", -260.0), ("L1_Cover", 0.55),
    ("L2_Bottom", -140.0), ("L2_Top", 200.0), ("L2_Cover", 0.38),
    ("L3_Bottom", 330.0), ("L3_Top", 800.0), ("L3_Cover", 0.5),
    ("L4_Bottom", 1100.0), ("L4_Top", 1900.0), ("L4_Cover", 0.55),
    ("LayerSoft", 0.28), ("ShapeScale", 520.0), ("BillowScale", 150.0), ("DetailScale", 42.0), ("DetailErosion", 0.3),
    ("EdgeSharpness", 5.0), ("NoiseLow", 0.38), ("NoiseHigh", 0.78),
    ("ClearInner", 90.0), ("ClearOuter", 420.0), ("WindX", 3.0), ("WindY", 1.0), ("DensityScale", 0.035),
]
CODE = r"""
float3 p = WP * 0.01;
float3 off = float3(WindX, WindY, 0.0) * T;
float n0 = Texture3DSampleLevel(Noise, NoiseSampler, (p + off * 0.5) / max(ShapeScale, 1.0), 0).r;
float n1 = Texture3DSampleLevel(Noise, NoiseSampler, (p + off) / max(BillowScale, 1.0), 0).r;
float n2 = Texture3DSampleLevel(Noise, NoiseSampler, (p + off * 1.5) / max(DetailScale, 1.0), 0).r;
float sr = n0 * 0.6 + n1 * 0.4;
float s = saturate(saturate((sr - NoiseLow) / max(NoiseHigh - NoiseLow, 0.01)) - (1.0 - n2) * DetailErosion);
float h = p.z;
float d = 0.0;
float4 lb = float4(L1_Bottom, L2_Bottom, L3_Bottom, L4_Bottom);
float4 lt = float4(L1_Top, L2_Top, L3_Top, L4_Top);
float4 lc = float4(L1_Cover, L2_Cover, L3_Cover, L4_Cover);
for (int i = 0; i < 4; i++)
{
    float th = max(lt[i] - lb[i], 1.0);
    float x = saturate((h - lb[i]) / th);
    float prof = saturate(x / LayerSoft) * saturate((1.0 - x) / (LayerSoft * 1.6));
    d += saturate((s * prof - (1.0 - lc[i])) * EdgeSharpness);
}
float clearMask = smoothstep(ClearInner, ClearOuter, length(p.xy));
return d * clearMask * DensityScale;
"""
c = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 0)
setp(c, "code", CODE); setp(c, "output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
names = ["WP", "T", "Noise"] + [n for n, _ in PARAMS]
ins = []
for nme in names:
    ci = unreal.CustomInput(); ci.set_editor_property("input_name", nme); ins.append(ci)
setp(c, "inputs", ins)
wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, -300)
tm = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -900, -230)
tx = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObject, -900, -160)
setp(tx, "texture", unreal.load_asset("/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128"))
ok = [MEL.connect_material_expressions(wp, "", c, "WP"), MEL.connect_material_expressions(tm, "", c, "T"), MEL.connect_material_expressions(tx, "", c, "Noise")]
y = -60
for nme, dv in PARAMS:
    e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, y)
    setp(e, "parameter_name", nme); setp(e, "default_value", dv); y += 70
    ok.append(MEL.connect_material_expressions(e, "", c, nme))
MEL.connect_material_property(c, "", unreal.MaterialProperty.MP_SUBSURFACE_COLOR)      # extinction
alb = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, -350)
setp(alb, "parameter_name", "CloudAlbedo"); setp(alb, "default_value", unreal.LinearColor(1.0, 0.93, 0.80, 1.0))
MEL.connect_material_property(alb, "", unreal.MaterialProperty.MP_BASE_COLOR)
glow = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, -550)
setp(glow, "parameter_name", "WarmGlow"); setp(glow, "default_value", unreal.LinearColor(0.9, 0.55, 0.25, 1.0))
gs = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, -750)
setp(gs, "parameter_name", "GlowStrength"); setp(gs, "default_value", 0.6)
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, -600)
MEL.connect_material_expressions(glow, "", mul, "A"); MEL.connect_material_expressions(gs, "", mul, "B")
mul2 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -100, -500)
MEL.connect_material_expressions(mul, "", mul2, "A"); MEL.connect_material_expressions(c, "", mul2, "B")
MEL.connect_material_property(mul2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
try:
    adv = MEL.create_material_expression(m, unreal.MaterialExpressionVolumetricAdvancedMaterialOutput, -200, 300)
    for k, v in [("const_phase_g", 0.5), ("const_multi_scattering_contribution", 0.8), ("const_multi_scattering_occlusion", 0.3),
                 ("const_multi_scattering_eccentricity", 0.4), ("multi_scattering_approximation_octave_count", 2)]:
        setp(adv, k, v)
except Exception as e:
    errs.append(("adv", repr(e)))
MEL.recompile_material(m); EAL.save_asset(MP, only_if_is_dirty=False)
mp = f"{DEST}/MI_PaintVolCloud"
mi = unreal.load_asset(mp) if EAL.does_asset_exist(mp) else AT.create_asset("MI_PaintVolCloud", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m); MEL.update_material_instance(mi); EAL.save_asset(mp, only_if_is_dirty=False)
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "VolumetricCloud":
        cc = a.get_component_by_class(unreal.VolumetricCloudComponent)
        setp(cc, "material", mi); setp(cc, "layer_bottom_altitude", 1.9); setp(cc, "layer_height", 3.2)
        setp(cc, "tracing_max_distance", 30.0); setp(cc, "view_sample_count_scale", 1.5)
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=18, yaw=0))
print("PV DONE connect_ok", all(ok), "errs", errs)
