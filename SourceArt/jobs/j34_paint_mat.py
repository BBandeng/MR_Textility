# BP_CloudWorld v4 - painterly puffy clouds in the same arrangement, black abyss below.
import unreal, json, math, random
REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("V4", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("V4 ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary; sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
def s2l(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def LC(r, g, b): return unreal.LinearColor(s2l(r), s2l(g), s2l(b), 1.0)

# ---------------------------------------------------------------- meshes
DEST = "/Game/PaintClouds"
def find_meshes():
    out = {}
    if EAL.does_directory_exist(DEST):
        for p in EAL.list_assets(DEST, recursive=True):
            a = unreal.load_asset(p.split(".")[0])
            if isinstance(a, unreal.StaticMesh): out[a.get_name()] = a
    return out
meshes = find_meshes()
if "AbyssBowl" not in meshes:
    src = unreal.InterchangeManager.create_source_data("C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/PaintClouds.glb")
    prm = unreal.ImportAssetParameters(); prm.is_automated = True
    unreal.InterchangeManager.get_interchange_manager_scripted().import_asset(DEST, src, prm)
    meshes = find_meshes()
log("meshes", sorted(meshes))
clouds = [meshes[k] for k in sorted(meshes) if k.startswith("PaintCloud_")]
bowl = meshes.get("AbyssBowl")
if not clouds or not bowl: raise RuntimeError("paint cloud meshes not imported")
cz = {m.get_name(): (m.get_bounding_box().min.z, m.get_bounding_box().max.z) for m in clouds}
log("cloud z ranges", cz)

# ---------------------------------------------------------------- materials
def new_mat(name):
    p = f"{DEST}/{name}"
    if EAL.does_asset_exist(p):
        m = unreal.load_asset(p); MEL.delete_all_material_expressions(m)
    else:
        m = AT.create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
    return m, p
def custom(m, code, out, names, x, y):
    c = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, x, y)
    setp(c, "code", code); setp(c, "output_type", out)
    ins = []
    for n in names:
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    setp(c, "inputs", ins); return c

m, M_CLOUD = new_mat("M_PaintCloud")
setp(m, "shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
setp(m, "blend_mode", unreal.BlendMode.BLEND_MASKED)
setp(m, "two_sided", False)
E = {}
E["N"] = MEL.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -1100, -300)
E["V"] = MEL.create_material_expression(m, unreal.MaterialExpressionCameraVectorWS, -1100, -230)
E["WP"] = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1100, -160)
E["OP"] = MEL.create_material_expression(m, unreal.MaterialExpressionObjectPositionWS, -1100, -90)
E["OR"] = MEL.create_material_expression(m, unreal.MaterialExpressionObjectRadius, -1100, -20)
E["Noise"] = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObject, -1100, 50)
setp(E["Noise"], "texture", unreal.load_asset("/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128"))
y = 150
for n, col in [("LightColor", (255, 234, 200)), ("MidA", (244, 156, 92)), ("MidB", (204, 96, 86)),
               ("ShadowA", (134, 108, 150)), ("ShadowB", (150, 76, 82)), ("CoolTint", (150, 176, 200))]:
    e = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -1100, y)
    setp(e, "parameter_name", n); setp(e, "default_value", LC(*col)); E[n] = e; y += 200
for n, d in [("SunWeight", 0.35), ("NoiseAmount", 0.95), ("EdgeLow", 0.05), ("EdgeHigh", 0.6), ("EdgeNoise", 0.65), ("Posterize", 0.3), ("CoolAmount", 0.6),
             ("AbyssDepth", 14000.0), ("AbyssDark", 0.22), ("Brightness", 1.0)]:
    e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -1100, y)
    setp(e, "parameter_name", n); setp(e, "default_value", d); E[n] = e; y += 90
COMMON = r"""
float3 q = (WP - OP) / max(OR, 1.0);
float hh = frac(sin(dot(OP.xy, float2(12.9898, 78.233)) * 0.001) * 43758.5453);
float n1 = Texture3DSampleLevel(Noise, NoiseSampler, q * 0.9 + hh * 7.0, 0).r;
float n2 = Texture3DSampleLevel(Noise, NoiseSampler, q * 2.7 + hh * 3.0, 0).r;
"""
COL = COMMON + r"""
float3 Ld = normalize(float3(0, 0, 1) * SunWeight + V * (1.0 - SunWeight));
float t = saturate(dot(normalize(N), Ld) * 0.5 + 0.5);
float tone = frac(hh * 5.3);
t = saturate(t * t * lerp(0.5, 0.95, tone) - 0.05 + (n1 - 0.5) * NoiseAmount + (n2 - 0.5) * NoiseAmount * 0.6);
t = lerp(t, floor(t * 6.0 + 0.5) / 6.0, Posterize);
float3 mid = lerp(MidA, MidB, hh);
float3 sh = lerp(ShadowA, ShadowB, frac(hh * 3.7));
float3 hi = lerp(LightColor, lerp(LightColor, mid, 0.55), smoothstep(0.45, 0.95, frac(hh * 9.1)));
float3 c = t < 0.5 ? lerp(sh, mid, t * 2.0) : lerp(mid, hi, (t - 0.5) * 2.0);
c = lerp(c, CoolTint, saturate((n2 - 0.55) * 1.6) * CoolAmount * (1.0 - t));
float f = saturate(1.0 + WP.z / max(AbyssDepth, 1.0));
return c * lerp(AbyssDark, 1.0, f) * Brightness;
"""
ALPHA = COMMON + r"""
float fres = saturate(dot(normalize(N), V));
float al = smoothstep(EdgeLow, EdgeHigh, fres + (n2 - 0.5) * EdgeNoise + (n1 - 0.5) * EdgeNoise * 0.5);
float2 px = Parameters.SvPosition.xy + float(ResolvedView.StateFrameIndexMod8) * 5.588238;
float ign = frac(52.9829189 * frac(dot(px, float2(0.06711056, 0.00583715))));
return al - ign + 0.3333;
"""
col = custom(m, COL, unreal.CustomMaterialOutputType.CMOT_FLOAT3,
             ["N", "V", "WP", "OP", "OR", "Noise", "LightColor", "MidA", "MidB", "ShadowA", "ShadowB", "SunWeight", "NoiseAmount", "AbyssDepth", "AbyssDark", "Brightness", "Posterize", "CoolTint", "CoolAmount"], -500, 0)
alp = custom(m, ALPHA, unreal.CustomMaterialOutputType.CMOT_FLOAT1,
             ["N", "V", "WP", "OP", "OR", "Noise", "EdgeLow", "EdgeHigh", "EdgeNoise"], -500, 700)
for c in (col, alp):
    for i in range(c.get_editor_property("inputs").__len__()):
        n = str(c.get_editor_property("inputs")[i].get_editor_property("input_name"))
        if not MEL.connect_material_expressions(E[n], "", c, n): err("connect", n)
MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
MEL.connect_material_property(alp, "", unreal.MaterialProperty.MP_OPACITY_MASK)
MEL.recompile_material(m); EAL.save_asset(M_CLOUD, only_if_is_dirty=False)
mi_p = f"{DEST}/MI_PaintCloud"
mi = unreal.load_asset(mi_p) if EAL.does_asset_exist(mi_p) else AT.create_asset("MI_PaintCloud", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m); MEL.update_material_instance(mi); EAL.save_asset(mi_p, only_if_is_dirty=False)


print("V4 MAT DONE errors=", len(rep["errors"]), rep["errors"])
