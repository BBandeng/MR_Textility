# BP_CloudWorld v2: cloud dome (panels on two shells, open apex for the sun),
# small irregular stepping clouds in the same flat material, clouds all around
# the player, non-walkable layers below.
import unreal, json, math, random

REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("CD", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("CD ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))

AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
ML = unreal.MathLibrary

# ---------------------------------------------------------------- import pieces
DEST = "/Game/Layer1/CloudPieces"
def find_pieces():
    out = {}
    if EAL.does_directory_exist(DEST):
        for p in EAL.list_assets(DEST, recursive=True):
            a = unreal.load_asset(p.split(".")[0])
            if isinstance(a, unreal.StaticMesh) and "CloudPiece_" in a.get_name():
                out[a.get_name()] = a
    return out
pieces = find_pieces()
if len(pieces) < 4:
    src = unreal.InterchangeManager.create_source_data("C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/CloudPieces.glb")
    prm = unreal.ImportAssetParameters(); prm.is_automated = True
    r = unreal.InterchangeManager.get_interchange_manager_scripted().import_asset(DEST, src, prm)
    log("import result", r)
    pieces = find_pieces()
log("pieces", sorted(pieces.keys()))
piece_list = [pieces[k] for k in sorted(pieces.keys())]
if not piece_list:
    raise RuntimeError("cloud pieces not imported")

# ---------------------------------------------------------------- materials
MPKG = "/Game/Layer1/Materials"
master = unreal.load_asset(f"{MPKG}/M_Cloud_BlenderLook")
mi_layer = unreal.load_asset(f"{MPKG}/MI_Cloud_BlenderLook")
p = f"{MPKG}/MI_Cloud_Invisible"
mi_inv = unreal.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(
    "MI_Cloud_Invisible", MPKG, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi_inv, master)
MEL.set_material_instance_scalar_parameter_value(mi_inv, "Opacity", 0.0)
MEL.update_material_instance(mi_inv); EAL.save_asset(p, only_if_is_dirty=False)

def variant(name, opacity):
    q = f"{MPKG}/{name}"
    v = unreal.load_asset(q) if EAL.does_asset_exist(q) else AT.create_asset(name, MPKG, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(v, mi_layer)
    MEL.set_material_instance_scalar_parameter_value(v, "Opacity", opacity)
    MEL.update_material_instance(v); EAL.save_asset(q, only_if_is_dirty=False)
    return v
mi_far = variant("MI_Cloud_Far", 0.32)
mi_step = variant("MI_Cloud_Step", 0.8)
canopy = unreal.load_asset("/Game/Layer1/Layer1_NoSun/StaticMeshes/Canopy___Continuous_mesh___80k_002")
cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder")
bb = canopy.get_bounding_box(); zmax = bb.max.z

# ---------------------------------------------------------------- blueprint
BP_PATH = "/Game/Layer1/Blueprints/BP_CloudWorld"
if EAL.does_asset_exist(BP_PATH):
    old = unreal.load_asset(BP_PATH)
    for a in list(EAS.get_all_level_actors()):
        if a.get_class() == old.generated_class():
            EAS.destroy_actor(a)
    EAL.delete_asset(BP_PATH)
fac = unreal.BlueprintFactory(); fac.set_editor_property("parent_class", unreal.Actor)
bp = AT.create_asset("BP_CloudWorld", "/Game/Layer1/Blueprints", unreal.Blueprint, fac)
root = sds.k2_gather_subobject_data_for_blueprint(bp)[0]

def add_mesh(name, mesh, mat, loc, rot, scale, collide=False):
    h, why = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp))
    if not SDL.is_handle_valid(h):
        err("add failed", name, str(why)); return
    sds.rename_subobject(h, unreal.Text(name))
    c = SDL.get_object(SDL.get_data(h))
    setp(c, "static_mesh", mesh)
    setp(c, "override_materials", [mat])
    setp(c, "relative_location", unreal.Vector(*loc))
    setp(c, "relative_rotation", rot)
    setp(c, "relative_scale3d", unreal.Vector(*scale))
    setp(c, "cast_shadow", False)
    try: c.set_collision_profile_name("BlockAll" if collide else "NoCollision")
    except Exception as e: err("collision", name, repr(e))
    if collide: setp(c, "hidden_in_game", True)

random.seed(21)
def R(roll=0, pitch=0, yaw=0): return unreal.Rotator(roll=roll, pitch=pitch, yaw=yaw)

# --- dome: canopy panels tangent to a sphere around the player, apex left open
DOME_CENTER_Z = -2000.0
#         name    radius  [(elevation deg, count, panel scale)]
SHELLS = [("Outer", 27000, [(-22, 6, 150), (4, 6, 150), (28, 5, 135), (48, 4, 105), (63, 3, 60)]),
          ("Inner", 19000, [(-8, 4, 95), (22, 3, 90), (50, 3, 55)])]
n_panels = 0
for sname, rd, rings in SHELLS:
    for ri, (elev, count, sc) in enumerate(rings):
        phase = random.uniform(0, 360)
        for k in range(count):
            az = phase + 360.0 * k / count + random.uniform(-8, 8)
            el = elev + random.uniform(-4, 4)
            e, a = math.radians(el), math.radians(az)
            loc = (rd * math.cos(e) * math.cos(a), rd * math.cos(e) * math.sin(a), DOME_CENTER_Z + rd * math.sin(e))
            rot = ML.compose_rotators(R(yaw=random.uniform(0, 360)), R(pitch=el - 90.0, yaw=az))
            s = sc * random.uniform(0.9, 1.1)
            add_mesh(f"Dome{sname}_{ri}_{k}", canopy, mi_layer if elev > 10 else mi_far, loc, rot, (s, s, s * 0.35))
            n_panels += 1
log("dome panels", n_panels)

# --- golden sky shell enclosing the whole dome (same painting as the level sky)
sky_mesh = unreal.load_asset("/Engine/EngineSky/SM_SkySphere")
sky_mat = unreal.load_asset("/Game/GoldenSky/M_Sky_Test2")
sb = sky_mesh.get_bounding_box(); log("sky mesh bbox", sb.min, sb.max)
add_mesh("GoldenShell", sky_mesh, sky_mat, (0, 0, DOME_CENTER_Z), R(), (11, 11, 11))

# --- layers below the player (top height in cm), never walkable
for n, sxy, sz, top, yaw, off in [("Below_Near", 200, 60, -1500, 40, (6000, 3000)), ("Below_Far", 420, 90, -9000, 120, (-8000, -5000))]:
    add_mesh(n, canopy, mi_far, (off[0], off[1], top - zmax * sz), R(yaw=yaw), (sxy, sxy, sz))

# --- stepping clouds: (x, y, top z, collision radius) in cm
STEPS = [(0, 0, 0, 170), (360, 90, 15, 130), (700, -60, 35, 140), (1040, 120, 20, 125), (1400, 30, 45, 150),
         (1750, -150, 30, 130), (2100, 20, 55, 140), (-330, -150, -15, 130), (-640, 60, -30, 135)]
for i, (x, y, z, r) in enumerate(STEPS):
    add_mesh(f"Step{i}_Collision", cyl, mi_inv, (x, y, z - 15), R(), (r / 50.0, r / 50.0, 0.3), collide=True)
    k = r / 100.0 * 1.15
    add_mesh(f"Step{i}_Cloud", random.choice(piece_list), mi_step, (x, y, z - 6), R(yaw=random.uniform(0, 360)), (k, k, 0.6))

# --- clouds around the player (no collision)
def near_step(x, y, d):
    return any(math.hypot(x - sx, y - sy) < d + sr for sx, sy, _, sr in STEPS)
n_near = 0
tries = 0
while n_near < 16 and tries < 2000:      # close: beside, above and below the path
    tries += 1
    x, y = random.uniform(-1800, 3200), random.uniform(-1500, 1500)
    band = random.choice(["side", "side", "above", "below"])
    if band == "side":
        if near_step(x, y, 350): continue
        z, s = random.uniform(-140, 120), random.uniform(1.2, 3.0)
    elif band == "above":
        z, s = random.uniform(450, 1300), random.uniform(2.5, 6.0)
    else:
        if near_step(x, y, 150): continue
        z, s = random.uniform(-900, -250), random.uniform(3.0, 7.0)
    add_mesh(f"Near_{n_near}", random.choice(piece_list), mi_layer, (x, y, z),
             R(roll=random.uniform(-15, 15), pitch=random.uniform(-15, 15), yaw=random.uniform(0, 360)), (s, s, s * 0.8))
    n_near += 1
for i in range(16):                      # mid distance: big drifting banks
    a, d = random.uniform(0, 2 * math.pi), random.uniform(4500, 14000)
    s = random.uniform(10, 32)
    add_mesh(f"Mid_{i}", random.choice(piece_list), mi_layer, (math.cos(a) * d, math.sin(a) * d, random.uniform(-2500, 5000)),
             R(roll=random.uniform(-20, 20), pitch=random.uniform(-20, 20), yaw=random.uniform(0, 360)), (s, s, s * 0.8))

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset(BP_PATH, only_if_is_dirty=False)

for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "Floor":
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        c.set_visibility(False); a.set_actor_hidden_in_game(True); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
act = EAS.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0))
act.set_actor_label("CloudWorld")
log("spawned, components", len(act.get_components_by_class(unreal.StaticMeshComponent)))

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def trace(x, y):
    try:
        hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 500), unreal.Vector(x, y, -3000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if hit is None: return None
        t = hit.to_tuple()
        return {"z": round(t[4].z, 1), "comp": t[10].get_name() if t[10] else None}
    except Exception as e:
        return "ERR " + repr(e)
for label, (x, y) in {"start": (0, 0), "step1": (360, 90), "step6": (2100, 20), "gap_0_1": (190, 48), "off": (0, 600), "far": (5000, 5000)}.items():
    log("trace", label, trace(x, y))

unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(-650, -300, 300), unreal.Rotator(roll=0, pitch=-20, yaw=22))
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
print("CD DONE errors=", len(rep["errors"]))
