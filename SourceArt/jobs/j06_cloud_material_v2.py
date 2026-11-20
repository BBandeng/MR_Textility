# Builds M_HeavenCloudVolume (multi-layer volumetric cloud material) and the
# BP_HeavenClouds Blueprint (VolumetricCloud + oil-paint post process + walkable
# invisible cloud floor), places it in the open level, and hides the old
# faceted Layer1 canopy meshes / grid floor / default VolumetricCloud.
import unreal, json

REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("HC", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("HC ERROR", s)
def setp(obj, name, val):
    try:
        obj.set_editor_property(name, val)
    except Exception as e:
        err("setprop", obj.get_class().get_name(), name, repr(e))

AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
PKG = "/Game/HeavenClouds"

# ---------------------------------------------------------------- material
M_PATH = f"{PKG}/M_HeavenCloudVolume"
if EAL.does_asset_exist(M_PATH):
    m = unreal.load_asset(M_PATH); MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_HeavenCloudVolume", PKG, unreal.Material, unreal.MaterialFactoryNew())
setp(m, "material_domain", unreal.MaterialDomain.MD_VOLUME)
setp(m, "blend_mode", unreal.BlendMode.BLEND_ADDITIVE)
setp(m, "shading_model", unreal.MaterialShadingModel.MSM_DEFAULT_LIT)
setp(m, "used_with_volumetric_cloud", True)

noise_tex = None
for cand in ["/Engine/EngineSky/VolumetricClouds/T_Volume_PerlinWorley_Balanced",
             "/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape128",
             "/Engine/EngineSky/VolumetricClouds/T_VolumeNoiseShape64"]:
    t = unreal.load_asset(cand)
    log("noise candidate", cand, t.get_class().get_name() if t else None)
    if t and isinstance(t, unreal.VolumeTexture):
        noise_tex = t; break

PARAMS = [  # name, default   (heights in metres, world Z; 0 = player's feet)
    ("L1_Bottom", -45.0), ("L1_Top", 2.5), ("L1_Soft", 4.0), ("L1_Coverage", 0.5), ("L1_Density", 1.0),
    ("L2_Bottom", 35.0), ("L2_Top", 85.0), ("L2_Soft", 15.0), ("L2_Coverage", 0.38), ("L2_Density", 0.6),
    ("L3_Bottom", 180.0), ("L3_Top", 260.0), ("L3_Soft", 30.0), ("L3_Coverage", 0.3), ("L3_Density", 0.35),
    ("ShapeScale", 60.0), ("ClumpScale", 6.0), ("DetailScale", 13.0), ("DetailErosion", 0.25), ("EdgeSharpness", 5.0),
    ("WindX", 2.0), ("WindY", 0.6), ("DensityScale", 0.06),
]

CODE = r"""
float3 p = WP * 0.01;
float3 off = float3(WindX, WindY, 0.0) * T;
float n0 = Texture3DSampleLevel(Noise, NoiseSampler, (p + off * 0.5) / max(ShapeScale * ClumpScale, 0.1), 0).r;
float n1 = Texture3DSampleLevel(Noise, NoiseSampler, (p + off) / max(ShapeScale, 0.1), 0).r;
float n2 = Texture3DSampleLevel(Noise, NoiseSampler, (p + off * 1.6) / max(DetailScale, 0.1), 0).r;
float s = saturate(n0 * 0.55 + n1 * 0.45 - (1.0 - n2) * DetailErosion);
float h = p.z;
float b1 = saturate((h - L1_Bottom) / max(L1_Soft, 0.01)) * saturate((L1_Top - h) / max(L1_Soft, 0.01));
float b2 = saturate((h - L2_Bottom) / max(L2_Soft, 0.01)) * saturate((L2_Top - h) / max(L2_Soft, 0.01));
float b3 = saturate((h - L3_Bottom) / max(L3_Soft, 0.01)) * saturate((L3_Top - h) / max(L3_Soft, 0.01));
float d1 = saturate((s * b1 - (1.0 - L1_Coverage)) * EdgeSharpness) * L1_Density;
float d2 = saturate((s * b2 - (1.0 - L2_Coverage)) * EdgeSharpness) * L2_Density;
float d3 = saturate((s * b3 - (1.0 - L3_Coverage)) * EdgeSharpness) * L3_Density;
return (d1 + d2 + d3) * DensityScale;
"""

custom = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -500, 0)
setp(custom, "code", CODE)
setp(custom, "output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT1)
setp(custom, "description", "HeavenCloudDensity")
input_names = ["WP", "T", "Noise"] + [n for n, _ in PARAMS]
def _ci(n):
    ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); return ci
setp(custom, "inputs", [_ci(n) for n in input_names])

wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, -400)
MEL.connect_material_expressions(wp, "", custom, "WP")
tm = MEL.create_material_expression(m, unreal.MaterialExpressionTime, -900, -330)
MEL.connect_material_expressions(tm, "", custom, "T")
tobj = MEL.create_material_expression(m, unreal.MaterialExpressionTextureObject, -900, -260)
if noise_tex:
    setp(tobj, "texture", noise_tex)
MEL.connect_material_expressions(tobj, "", custom, "Noise")
y = -150
for n, d in PARAMS:
    sp = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, y)
    setp(sp, "parameter_name", n); setp(sp, "default_value", d)
    grp = "Layer1 CloudSea" if n.startswith("L1") else "Layer2 Mid" if n.startswith("L2") else "Layer3 High" if n.startswith("L3") else "Shape & Wind"
    setp(sp, "group", grp)
    MEL.connect_material_expressions(sp, "", custom, n)
    y += 70

# extinction
MEL.connect_material_property(custom, "", unreal.MaterialProperty.MP_SUBSURFACE_COLOR)
# albedo
alb = MEL.create_material_expression(m, unreal.MaterialExpressionVectorParameter, -500, -300)
setp(alb, "parameter_name", "CloudAlbedo"); setp(alb, "group", "Look")
setp(alb, "default_value", unreal.LinearColor(1.0, 0.94, 0.86, 1.0))
MEL.connect_material_property(alb, "", unreal.MaterialProperty.MP_BASE_COLOR)
# multiple scattering so shadowed parts stay soft & bright (painterly)
try:
    adv = MEL.create_material_expression(m, unreal.MaterialExpressionVolumetricAdvancedMaterialOutput, -200, 300)
    for k, v in [("const_phase_g", 0.55), ("const_multi_scattering_contribution", 0.6),
                 ("const_multi_scattering_occlusion", 0.4), ("const_multi_scattering_eccentricity", 0.5),
                 ("multi_scattering_approximation_octave_count", 2)]:
        setp(adv, k, v)
except Exception as e:
    err("advanced output", repr(e))

MEL.recompile_material(m)
EAL.save_asset(M_PATH, only_if_is_dirty=False)
log("material ok", M_PATH)

MI_PATH = f"{PKG}/MI_HeavenCloudVolume"
mi = unreal.load_asset(MI_PATH) if EAL.does_asset_exist(MI_PATH) else AT.create_asset(
    "MI_HeavenCloudVolume", PKG, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi, m)
MEL.update_material_instance(mi)
EAL.save_asset(MI_PATH, only_if_is_dirty=False)
log("material instance ok", MI_PATH)


ues = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
ues.set_level_viewport_camera_info(unreal.Vector(0, -3000, 2500), unreal.Rotator(roll=0, pitch=-25, yaw=90))
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
print("HC MAT DONE errors=", len(rep["errors"]))
