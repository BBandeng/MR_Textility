# Painted-look volumetric clouds in several stacked layers; remove gold-leaf shards.
import unreal, json
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("VL", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("VL ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
DEST = "/Game/PaintClouds"

MP = f"{DEST}/M_VolCloudLayers"
if EAL.does_asset_exist(MP):
    m = unreal.load_asset(MP); MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_VolCloudLayers", DEST, unreal.Material, unreal.MaterialFactoryNew())
setp(m, "material_domain", unreal.MaterialDomain.MD_VOLUME)
setp(m, "blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
setp(m, "used_with_volumetric_cloud", True)

PARAMS = [("Coverage", 0.62), ("DensityScale", 0.035), ("ShapeScale", 260.0), ("ClumpScale", 3.5), ("DetailScale", 55.0),
          ("DetailErosion", 0.3), ("EdgeSharpness", 6.0), ("NoiseLow", 0.42), ("NoiseHigh", 0.62), ("HoleRadius", 260.0), ("Wind", 3.0), ("HeightFalloff", 0.5)]
CODE = r"""
struct FN
{
    float h(float3 p) { return frac(sin(dot(p, float3(127.1, 311.7, 74.7))) * 43758.5453); }
    float n(float3 x)
    {
        float3 i = floor(x); float3 f = frac(x); f = f * f * (3.0 - 2.0 * f);
        return lerp(lerp(lerp(h(i), h(i + float3(1, 0, 0)), f.x), lerp(h(i + float3(0, 1, 0)), h(i + float3(1, 1, 0)), f.x), f.y),
                    lerp(lerp(h(i + float3(0, 0, 1)), h(i + float3(1, 0, 1)), f.x), lerp(h(i + float3(0, 1, 1)), h(i + float3(1, 1, 1)), f.x), f.y), f.z);
    }
    float fbm(float3 x) { return n(x) * 0.55 + n(x * 2.03 + 11.3) * 0.3 + n(x * 4.11 + 5.7) * 0.15; }
};
FN N;
float3 p = WP * 0.01;
p.xy += float2(Wind, Wind * 0.3) * T;
const float LB[5] = { -950.0, -300.0, 140.0, 700.0, 1500.0 };
const float LT[5] = { -480.0,   -5.0, 520.0, 1200.0, 2300.0 };
float dsum = 0.0;
for (int i = 0; i < 5; i++)
{
    float h01 = (p.z - LB[i]) / (LT[i] - LB[i]);
    if (h01 > 0.0 && h01 < 1.0)
    {
        float3 q = p + float3(i * 371.0, i * 197.0, 0.0);
        float n0 = N.fbm(q / (ShapeScale * ClumpScale));
        float n1 = N.fbm(q / ShapeScale);
        float n2 = N.n(q / DetailScale) * 0.6 + N.n(q / DetailScale * 2.7) * 0.4;
        float s = saturate((n0 * 0.6 + n1 * 0.4 - NoiseLow) / max(NoiseHigh - NoiseLow, 0.01));
        float d = saturate((s - (1.0 - Coverage) - h01 * HeightFalloff) * EdgeSharpness) * saturate(h01 / 0.06);
        d = saturate(d - (1.0 - n2) * DetailErosion * (1.0 - d * 0.5));
        dsum += d;
    }
}
if (p.z > 60.0 && p.z < 600.0)
{
    dsum *= saturate((length(p.xy) - HoleRadius) / (HoleRadius * 0.5));
}
return dsum * DensityScale;
"""
c = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 0)
setp(c, "code", CODE); setp(c, "output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1); setp(c, "description", "LayeredCloudDensity")
names = ["WP", "T", "Noise"] + [n for n, _ in PARAMS]
ins = []
for n in names:
    ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
setp(c, "inputs", ins)
wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -950, -300)
tm = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -950, -230)
tx = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObject, -950, -160)
setp(tx, "texture", unreal.load_asset("/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128"))
ok = [MEL.connect_material_expressions(wp, "", c, "WP"), MEL.connect_material_expressions(tm, "", c, "T"), MEL.connect_material_expressions(tx, "", c, "Noise")]
y = -60
for n, d in PARAMS:
    e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -950, y)
    setp(e, "parameter_name", n); setp(e, "default_value", d); ok.append(MEL.connect_material_expressions(e, "", c, n)); y += 80
log("connections", all(ok))
MEL.connect_material_property(c, "", unreal.MaterialProperty.MP_SUBSURFACE_COLOR)       # extinction
alb = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, -350)
setp(alb, "parameter_name", "CloudAlbedo"); setp(alb, "default_value", unreal.LinearColor(1.0, 0.9, 0.74, 1.0))
MEL.connect_material_property(alb, "", unreal.MaterialProperty.MP_BASE_COLOR)
glow = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, 400)
setp(glow, "parameter_name", "WarmGlow"); setp(glow, "default_value", unreal.LinearColor(0.9, 0.5, 0.28, 1.0))
gs = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -500, 600)
setp(gs, "parameter_name", "WarmGlowStrength"); setp(gs, "default_value", 0.14)
m1 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, 400)
MEL.connect_material_expressions(glow, "", m1, "A"); MEL.connect_material_expressions(gs, "", m1, "B")
m2 = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -100, 400)
MEL.connect_material_expressions(m1, "", m2, "A"); MEL.connect_material_expressions(c, "", m2, "B")
MEL.connect_material_property(m2, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
try:
    adv = MEL.create_material_expression(m, unreal.MaterialExpressionVolumetricAdvancedMaterialOutput, -200, 700)
    for k, v in [("const_phase_g", 0.5), ("const_multi_scattering_contribution", 0.7), ("const_multi_scattering_occlusion", 0.3),
                 ("const_multi_scattering_eccentricity", 0.5), ("multi_scattering_approximation_octave_count", 2)]:
        setp(adv, k, v)
except Exception as e:
    err("advanced output", repr(e))
MEL.recompile_material(m); EAL.save_asset(MP, only_if_is_dirty=False)
mip = f"{DEST}/MI_VolCloudLayers"
mi = unreal.load_asset(mip) if EAL.does_asset_exist(mip) else AT.create_asset("MI_VolCloudLayers", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m); MEL.clear_all_material_instance_parameters(mi); MEL.update_material_instance(mi); EAL.save_asset(mip, only_if_is_dirty=False)

for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "VolumetricCloud":
        vc = a.get_component_by_class(unreal.VolumetricCloudComponent)
        setp(vc, "material", mi); setp(vc, "layer_bottom_altitude", 2.0); setp(vc, "layer_height", 3.3)
        setp(vc, "view_sample_count_scale", 2.0)
        vc.set_visibility(True); log("volumetric cloud configured")

# ---- remove gold-leaf shards from the Blueprint
bp = unreal.load_asset("/Game/Layer1/Blueprints/BP_CloudWorld")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); SDL = unreal.SubobjectDataBlueprintFunctionLibrary
hs = sds.k2_gather_subobject_data_for_blueprint(bp)
gold = []
for h in hs:
    o = SDL.get_object(SDL.get_data(h))
    if isinstance(o, unreal.StaticMeshComponent):
        mats = o.get_editor_property("override_materials")
        if mats and mats[0] and mats[0].get_name() in ("MI_Shard_1", "MI_Shard_3"):
            gold.append((h, o))
removed = 0
try:
    removed = sds.delete_subobjects(hs[0], [h for h, _ in gold], bp)
except Exception as e:
    err("delete_subobjects", repr(e))
if not removed:
    for _, o in gold:
        setp(o, "visible", False); setp(o, "hidden_in_game", True)
log("gold shards", len(gold), "deleted", removed)
unreal.BlueprintEditorLibrary.compile_blueprint(bp); EAL.save_asset(bp.get_path_name(), only_if_is_dirty=False)

unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=12, yaw=0))
json.dump(rep, open("C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("VL DONE errors=", len(rep["errors"]), rep["errors"])
