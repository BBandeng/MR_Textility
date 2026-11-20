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

mi = unreal.load_asset(f"{DEST}/MI_PaintCloud")
M_ABYSS = f"{DEST}/M_Abyss"
if mi is None: raise RuntimeError("MI_PaintCloud missing")
inv_p = "/Game/Layer1/Materials/MI_Cloud_Invisible"
mi_inv = unreal.load_asset(inv_p)
cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder")

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
def puff(name, loc, s, flat=0.75):
    add_mesh(name, random.choice(clouds), mi, loc, R(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(0, 360)),
             (s * random.uniform(0.85, 1.2), s * random.uniform(0.85, 1.2), s * flat * random.uniform(0.8, 1.2)))

add_mesh("Abyss", bowl, unreal.load_asset(M_ABYSS), (0, 0, 0), R(), (1000, 1000, 1000))

# --- top of the dome: three rings of clouds (centre left open for the sun)
for n, r_out, zc, off, k, smin, smax in [("Sky_Low", 22000, 7500, (0, 0), 24, 32, 62),
        ("Sky_Mid", 33800, 15000, (-3000, 2000), 28, 50, 95), ("Sky_High", 49400, 24500, (2500, -3500), 30, 75, 135)]:
    for i in range(k):
        a = 2 * math.pi * (i + random.uniform(-0.35, 0.35)) / k; d = r_out * random.uniform(0.38, 1.0)
        s = random.uniform(smin, smax)
        puff(f"{n}_{i}", (off[0] + math.cos(a) * d, off[1] + math.sin(a) * d, zc + random.uniform(-0.12, 0.12) * r_out), s)
# --- sides of the dome
RD, CZ = 30000.0, -3000.0
for ri, (elev, cnt) in enumerate([(-24, 6), (0, 6), (24, 5)]):
    phase = random.uniform(0, 360)
    for k in range(cnt):
        az = math.radians(phase + 360.0 * k / cnt + random.uniform(-8, 8)); el = math.radians(elev + random.uniform(-4, 4))
        rad = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
        t1 = (-math.sin(az), math.cos(az), 0.0)
        t2 = (rad[1] * t1[2] - rad[2] * t1[1], rad[2] * t1[0] - rad[0] * t1[2], rad[0] * t1[1] - rad[1] * t1[0])
        for j in range(6):
            u, v, w = random.uniform(-14000, 14000), random.uniform(-14000, 14000), random.uniform(-3000, 3000)
            loc = tuple(CZ * (1 if i == 2 else 0) + rad[i] * (RD + w) + t1[i] * u + t2[i] * v for i in range(3))
            puff(f"DomeSide_{ri}_{k}_{j}", loc, random.uniform(42, 88))
# --- cloud layers down in the abyss, never walkable
for n, r_out, top, off, k, smin, smax in [("Below_Near", 26000, -1500, (6000, 3000), 20, 35, 70), ("Below_Far", 54000, -9000, (-8000, -5000), 26, 75, 140)]:
    for i in range(k):
        a = random.uniform(0, 2 * math.pi); d = r_out * math.sqrt(random.uniform(0.02, 1.0)); s = random.uniform(smin, smax)
        puff(f"{n}_{i}", (off[0] + math.cos(a) * d, off[1] + math.sin(a) * d, top - s * 75 - random.uniform(0, 2500)), s)

# --- stepping clouds: (x, y, top z, collision radius) cm
STEPS = [(0, 0, 0, 170), (360, 90, 15, 130), (700, -60, 35, 140), (1040, 120, 20, 125), (1400, 30, 45, 150),
         (1750, -150, 30, 130), (2100, 20, 55, 140), (-330, -150, -15, 130), (-640, 60, -30, 135)]
for i, (x, y, z, r) in enumerate(STEPS):
    add_mesh(f"Step{i}_Collision", cyl, mi_inv, (x, y, z - 15), R(), (r / 50.0, r / 50.0, 0.3), collide=True)
    mesh = random.choice(clouds); k = r / 100.0 * 1.35; kz = k * 0.45
    add_mesh(f"Step{i}_Cloud", mesh, mi, (x, y, z + 12 - cz[mesh.get_name()][1] * kz), R(yaw=random.uniform(0, 360)), (k, k, kz))

# --- clouds around the player
def near_step(x, y, d): return any(math.hypot(x - sx, y - sy) < d + sr for sx, sy, _, sr in STEPS)
n = 0; tries = 0
while n < 36 and tries < 5000:
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
for i in range(34):
    a, d = random.uniform(0, 2 * math.pi), random.uniform(4500, 15000)
    puff(f"Mid_{i}", (math.cos(a) * d, math.sin(a) * d, random.uniform(-2500, 5000)), random.uniform(10, 35))

unreal.BlueprintEditorLibrary.compile_blueprint(bp); EAL.save_asset(BP_PATH, only_if_is_dirty=False)
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "ExponentialHeightFog":
        l = a.get_actor_location(); a.set_actor_location(unreal.Vector(l.x, l.y, -200000.0), False, False); log("height fog lowered to z=-200000 (was -6850)")
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
print("V4 DONE errors=", len(rep["errors"]))
