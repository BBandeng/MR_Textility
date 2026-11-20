# BP_CloudWorld v5 - collage: flat painted cloud cut-outs, same arrangement, black abyss.
import unreal, json, math, random
REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("V5", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("V5 ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary; sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
ML = unreal.MathLibrary
DEST = "/Game/PaintClouds"

# ---------------------------------------------------------------- textures
tasks = []
for k in range(1, 7):
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", f"C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/cloud_sprites/T_PaintCloud_{k}.png")
    t.set_editor_property("destination_path", DEST + "/Sprites")
    t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
    tasks.append(t)
AT.import_asset_tasks(tasks)
texs = [unreal.load_asset(f"{DEST}/Sprites/T_PaintCloud_{k}") for k in range(1, 7)]
log("textures", [t.get_name() if t else None for t in texs])
texs = [t for t in texs if t]
if not texs: raise RuntimeError("sprites not imported")

# ---------------------------------------------------------------- material
MP = f"{DEST}/M_CloudCard"
if EAL.does_asset_exist(MP):
    m = unreal.load_asset(MP); MEL.delete_all_material_expressions(m)
else:
    m = AT.create_asset("M_CloudCard", DEST, unreal.Material, unreal.MaterialFactoryNew())
setp(m, "shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
setp(m, "blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
setp(m, "two_sided", True)
tex = MEL.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -900, 0)
setp(tex, "parameter_name", "Cloud"); setp(tex, "texture", texs[0])
wp = MEL.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -900, 300)
P = {}
y = 420
for n, d in [("AbyssDepth", 14000.0), ("AbyssDark", 0.25), ("Brightness", 1.0), ("Opacity", 1.0)]:
    e = MEL.create_material_expression(m, unreal.MaterialExpressionScalarParameter, -900, y)
    setp(e, "parameter_name", n); setp(e, "default_value", d); P[n] = e; y += 90
def custom(code, out, names, y):
    c = MEL.create_material_expression(m, unreal.MaterialExpressionCustom, -450, y)
    setp(c, "code", code); setp(c, "output_type", out)
    ins = []
    for n in names:
        ci = unreal.CustomInput(); ci.set_editor_property("input_name", n); ins.append(ci)
    setp(c, "inputs", ins); return c
col = custom("float f = saturate(1.0 + WP.z / max(AbyssDepth, 1.0)); return Tex * lerp(AbyssDark, 1.0, f) * Brightness;",
             unreal.CustomMaterialOutputType.CMOT_FLOAT3, ["Tex", "WP", "AbyssDepth", "AbyssDark", "Brightness"], 0)
ok = [MEL.connect_material_expressions(tex, "RGB", col, "Tex"), MEL.connect_material_expressions(wp, "", col, "WP")]
for n in ["AbyssDepth", "AbyssDark", "Brightness"]: ok.append(MEL.connect_material_expressions(P[n], "", col, n))
MEL.connect_material_property(col, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
mul = MEL.create_material_expression(m, unreal.MaterialExpressionMultiply, -450, 400)
ok += [MEL.connect_material_expressions(tex, "A", mul, "A"), MEL.connect_material_expressions(P["Opacity"], "", mul, "B")]
MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_OPACITY)
log("connections", ok)
MEL.recompile_material(m); EAL.save_asset(MP, only_if_is_dirty=False)
mis = []
for i, t in enumerate(texs):
    p = f"{DEST}/MI_CloudCard_{i + 1}"
    mi = unreal.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(f"MI_CloudCard_{i + 1}", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, m); MEL.set_material_instance_texture_parameter_value(mi, "Cloud", t)
    MEL.update_material_instance(mi); EAL.save_asset(p, only_if_is_dirty=False); mis.append(mi)

plane = unreal.load_asset("/Engine/BasicShapes/Plane")
cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder")
mi_inv = unreal.load_asset("/Game/Layer1/Materials/MI_Cloud_Invisible")
bowl = unreal.load_asset(f"{DEST}/PaintClouds/StaticMeshes/AbyssBowl")
if bowl is None:
    for p in EAL.list_assets(DEST, recursive=True):
        if "AbyssBowl" in p: bowl = unreal.load_asset(p.split(".")[0])
abyss_mat = unreal.load_asset(f"{DEST}/M_Abyss")

# ---------------------------------------------------------------- blueprint
BP_PATH = "/Game/Layer1/Blueprints/BP_CloudWorld"
if EAL.does_asset_exist(BP_PATH):
    old = unreal.load_asset(BP_PATH)
    for a in list(EAS.get_all_level_actors()):
        if a.get_class() == old.generated_class(): EAS.destroy_actor(a)
    EAL.delete_asset(BP_PATH)
fac = unreal.BlueprintFactory(); fac.set_editor_property("parent_class", unreal.Actor)
bp = AT.create_asset("BP_CloudWorld", "/Game/Layer1/Blueprints", unreal.Blueprint, fac)
root = sds.k2_gather_subobject_data_for_blueprint(bp)[0]
def R(roll=0, pitch=0, yaw=0): return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)
count = [0]
def add_mesh(name, mesh, mat, loc, rot, scale, collide=False):
    h, why = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp))
    if not SDL.is_handle_valid(h): err("add failed", name, str(why)); return
    sds.rename_subobject(h, unreal.Text(name))
    c = SDL.get_object(SDL.get_data(h))
    setp(c, "static_mesh", mesh); setp(c, "override_materials", [mat])
    setp(c, "relative_location", unreal.Vector(*loc)); setp(c, "relative_rotation", rot); setp(c, "relative_scale3d", unreal.Vector(*scale))
    setp(c, "cast_shadow", False)
    try: c.set_collision_profile_name("BlockAll" if collide else "NoCollision")
    except Exception as e: err("collision", name, repr(e))
    if collide: setp(c, "hidden_in_game", True)
    count[0] += 1
random.seed(52)
TARGET = (0.0, 0.0, 170.0)
def face_rot(loc):
    d = [TARGET[i] - loc[i] + random.uniform(-0.12, 0.12) * 1.0 for i in range(3)]
    d = [TARGET[i] - loc[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in d)) or 1.0
    z = [v / n for v in d]
    z = [z[0] + random.uniform(-0.2, 0.2), z[1] + random.uniform(-0.2, 0.2), z[2] + random.uniform(-0.1, 0.1)]
    n = math.sqrt(sum(v * v for v in z)); z = [v / n for v in z]
    if abs(z[2]) > 0.85:
        a = random.uniform(0, 2 * math.pi); x = [math.cos(a), math.sin(a), 0.0]
    else:
        x = [z[1] * 1 - z[2] * 0, z[2] * 0 - z[0] * 1, 0.0]      # cross(z, up)
    return ML.make_rot_from_zx(unreal.Vector(*z), unreal.Vector(*x))
def puff(name, loc, s, flat=None):
    w = s * 2.7 * random.uniform(0.85, 1.2)
    add_mesh(name, plane, random.choice(mis), loc, face_rot(loc), (w * random.choice([1, -1]), w, 1.0))

if bowl and abyss_mat: add_mesh("Abyss", bowl, abyss_mat, (0, 0, 0), R(), (1000, 1000, 1000))
else: err("abyss assets missing")

for n, r_out, zc, off, k, smin, smax in [("Sky_Low", 22000, 7500, (0, 0), 14, 32, 62),
        ("Sky_Mid", 33800, 15000, (-3000, 2000), 16, 50, 95), ("Sky_High", 49400, 24500, (2500, -3500), 18, 75, 135)]:
    for i in range(k):
        a = 2 * math.pi * (i + random.uniform(-0.35, 0.35)) / k; d = r_out * random.uniform(0.38, 1.0)
        puff(f"{n}_{i}", (off[0] + math.cos(a) * d, off[1] + math.sin(a) * d, zc + random.uniform(-0.12, 0.12) * r_out), random.uniform(smin, smax))
RD, CZ = 30000.0, -3000.0
for ri, (elev, cnt) in enumerate([(-24, 6), (0, 6), (24, 5)]):
    phase = random.uniform(0, 360)
    for k in range(cnt):
        az = math.radians(phase + 360.0 * k / cnt + random.uniform(-8, 8)); el = math.radians(elev + random.uniform(-4, 4))
        rad = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
        t1 = (-math.sin(az), math.cos(az), 0.0)
        t2 = (rad[1] * t1[2] - rad[2] * t1[1], rad[2] * t1[0] - rad[0] * t1[2], rad[0] * t1[1] - rad[1] * t1[0])
        for j in range(4):
            u, v, w = random.uniform(-14000, 14000), random.uniform(-14000, 14000), random.uniform(-3000, 3000)
            loc = tuple(CZ * (1 if i == 2 else 0) + rad[i] * (RD + w) + t1[i] * u + t2[i] * v for i in range(3))
            puff(f"DomeSide_{ri}_{k}_{j}", loc, random.uniform(42, 88))
for n, r_out, top, off, k, smin, smax in [("Below_Near", 26000, -1500, (6000, 3000), 12, 35, 70), ("Below_Far", 54000, -9000, (-8000, -5000), 16, 75, 140)]:
    for i in range(k):
        a = random.uniform(0, 2 * math.pi); d = r_out * math.sqrt(random.uniform(0.02, 1.0)); s = random.uniform(smin, smax)
        puff(f"{n}_{i}", (off[0] + math.cos(a) * d, off[1] + math.sin(a) * d, top - 500 - random.uniform(0, 3500)), s)

STEPS = [(0, 0, 0, 170), (360, 90, 15, 130), (700, -60, 35, 140), (1040, 120, 20, 125), (1400, 30, 45, 150),
         (1750, -150, 30, 130), (2100, 20, 55, 140), (-330, -150, -15, 130), (-640, 60, -30, 135)]
for i, (x, y, z, r) in enumerate(STEPS):
    add_mesh(f"Step{i}_Collision", cyl, mi_inv, (x, y, z - 15), R(), (r / 50.0, r / 50.0, 0.3), collide=True)
    k = r / 50.0 * 1.6
    add_mesh(f"Step{i}_Cloud", plane, random.choice(mis), (x, y, z + 2), R(yaw=random.uniform(0, 360)), (k, k, 1.0))

def near_step(x, y, d): return any(math.hypot(x - sx, y - sy) < d + sr for sx, sy, _, sr in STEPS)
n = 0; tries = 0
while n < 22 and tries < 3000:
    tries += 1
    x, y = random.uniform(-2000, 3400), random.uniform(-1700, 1700)
    band = random.choice(["side", "side", "above", "below"])
    if band == "side":
        s = random.uniform(1.5, 4.0)
        if near_step(x, y, 150 + s * 100): continue
        z = random.uniform(-100, 320)
    elif band == "above": z, s = random.uniform(600, 1500), random.uniform(3.0, 7.0)
    else:
        s = random.uniform(3.0, 7.0)
        if near_step(x, y, 100): continue
        z = random.uniform(-1300, -500)
    puff(f"Near_{n}", (x, y, z), s); n += 1
for i in range(20):
    a, d = random.uniform(0, 2 * math.pi), random.uniform(4500, 15000)
    puff(f"Mid_{i}", (math.cos(a) * d, math.sin(a) * d, random.uniform(-2500, 5000)), random.uniform(10, 35))

unreal.BlueprintEditorLibrary.compile_blueprint(bp); EAL.save_asset(BP_PATH, only_if_is_dirty=False)
act = EAS.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0)); act.set_actor_label("CloudWorld")
log("components", count[0])
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def trace(x, y):
    try:
        hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 500), unreal.Vector(x, y, -3000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if hit is None: return None
        t = hit.to_tuple(); return {"z": round(t[4].z, 1), "comp": t[10].get_name() if t[10] else None}
    except Exception as e: return "ERR " + repr(e)
for label, (x, y) in {"start": (0, 0), "step1": (360, 90), "gap": (190, 48), "off": (0, 600)}.items():
    log("trace", label, trace(x, y))
with open(REPORT, "w", encoding="utf-8") as f: json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
print("V5 DONE errors=", len(rep["errors"]))
