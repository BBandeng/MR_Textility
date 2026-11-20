# BP_CloudWorld v3 - everything uses the Blender canopy cloud (whole sheet or
# fragments cut from it) with the same flat material.
import unreal, json, math, random
REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("V3", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("V3 ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary; sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
ML = unreal.MathLibrary

DEST = "/Game/Layer1/CanopyPieces"
def find_pieces():
    out = {}
    if EAL.does_directory_exist(DEST):
        for p in EAL.list_assets(DEST, recursive=True):
            a = unreal.load_asset(p.split(".")[0])
            if isinstance(a, unreal.StaticMesh) and "CanopyPiece_" in a.get_name(): out[a.get_name()] = a
    return out
pieces = find_pieces()
if len(pieces) < 6:
    src = unreal.InterchangeManager.create_source_data("C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/CanopyPieces.glb")
    prm = unreal.ImportAssetParameters(); prm.is_automated = True
    unreal.InterchangeManager.get_interchange_manager_scripted().import_asset(DEST, src, prm)
    pieces = find_pieces()
piece_list = [pieces[k] for k in sorted(pieces)]
log("pieces", sorted(pieces))
if not piece_list: raise RuntimeError("canopy pieces not imported")

MPKG = "/Game/Layer1/Materials"
master = unreal.load_asset(f"{MPKG}/M_Cloud_BlenderLook")
mi_layer = unreal.load_asset(f"{MPKG}/MI_Cloud_BlenderLook")
p = f"{MPKG}/MI_Cloud_Invisible"
mi_inv = unreal.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset("MI_Cloud_Invisible", MPKG, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
MEL.set_material_instance_parent(mi_inv, master); MEL.set_material_instance_scalar_parameter_value(mi_inv, "Opacity", 0.0)
MEL.update_material_instance(mi_inv); EAL.save_asset(p, only_if_is_dirty=False)

canopy = unreal.load_asset("/Game/Layer1/Layer1_NoSun/StaticMeshes/Canopy___Continuous_mesh___80k_002")
cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder")
bb = canopy.get_bounding_box(); zmin, zmax = bb.min.z, bb.max.z

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
random.seed(33)

# --- top of the dome: the three layers from the previous version
for n, sxy, sz, bottom, yaw, roll, pitch, off in [("Sky_Low", 170, 70, 3500, 0, 6, 0, (0, 0)),
        ("Sky_Mid", 260, 80, 11000, 75, 0, -4, (-3000, 2000)), ("Sky_High", 380, 90, 20000, 160, 3, 3, (2500, -3500))]:
    add_mesh(n, canopy, mi_layer, (off[0], off[1], bottom - zmin * sz), R(roll, pitch, yaw), (sxy, sxy, sz))
# --- sides of the dome: panels leaning inward, curving down past the horizon
RD, CZ = 30000.0, -3000.0
for ri, (elev, count, sc) in enumerate([(-24, 6, 150), (0, 6, 150), (24, 5, 140)]):
    phase = random.uniform(0, 360)
    for k in range(count):
        az = phase + 360.0 * k / count + random.uniform(-8, 8); el = elev + random.uniform(-4, 4)
        e, a = math.radians(el), math.radians(az)
        loc = (RD * math.cos(e) * math.cos(a), RD * math.cos(e) * math.sin(a), CZ + RD * math.sin(e))
        rot = ML.compose_rotators(R(yaw=random.uniform(0, 360)), R(pitch=el - 90.0, yaw=az))
        s = sc * random.uniform(0.9, 1.1)
        add_mesh(f"DomeSide_{ri}_{k}", canopy, mi_layer, loc, rot, (s, s, s * 0.35))
# --- layers below, never walkable
for n, sxy, sz, top, yaw, pitch, off in [("Below_Near", 200, 60, -1500, 40, -5, (6000, 3000)), ("Below_Far", 420, 90, -9000, 120, 0, (-8000, -5000))]:
    add_mesh(n, canopy, mi_layer, (off[0], off[1], top - zmax * sz), R(0, pitch, yaw), (sxy, sxy, sz))

# --- stepping clouds: (x, y, top z, collision radius) cm
STEPS = [(0, 0, 0, 170), (360, 90, 15, 130), (700, -60, 35, 140), (1040, 120, 20, 125), (1400, 30, 45, 150),
         (1750, -150, 30, 130), (2100, 20, 55, 140), (-330, -150, -15, 130), (-640, 60, -30, 135)]
for i, (x, y, z, r) in enumerate(STEPS):
    add_mesh(f"Step{i}_Collision", cyl, mi_inv, (x, y, z - 15), R(), (r / 50.0, r / 50.0, 0.3), collide=True)
    k = r / 100.0 * 1.2
    add_mesh(f"Step{i}_Cloud", random.choice(piece_list), mi_layer, (x, y, z), R(yaw=random.uniform(0, 360)), (k, k, k * 0.45))

# --- clouds around the player, same cloud fragments, no collision
def near_step(x, y, d): return any(math.hypot(x - sx, y - sy) < d + sr for sx, sy, _, sr in STEPS)
n = 0; tries = 0
while n < 22 and tries < 3000:
    tries += 1
    x, y = random.uniform(-2000, 3400), random.uniform(-1700, 1700)
    band = random.choice(["side", "side", "above", "below"])
    if band == "side":
        if near_step(x, y, 300): continue
        z, s = random.uniform(-100, 320), random.uniform(1.5, 4.0)
    elif band == "above": z, s = random.uniform(450, 1400), random.uniform(3.0, 7.0)
    else:
        if near_step(x, y, 150): continue
        z, s = random.uniform(-900, -250), random.uniform(3.0, 7.0)
    add_mesh(f"Near_{n}", random.choice(piece_list), mi_layer, (x, y, z), R(random.uniform(-20, 20), random.uniform(-20, 20), random.uniform(0, 360)), (s, s, s * 0.7)); n += 1
for i in range(20):
    a, d = random.uniform(0, 2 * math.pi), random.uniform(4000, 15000); s = random.uniform(10, 35)
    add_mesh(f"Mid_{i}", random.choice(piece_list), mi_layer, (math.cos(a) * d, math.sin(a) * d, random.uniform(-2500, 5000)),
             R(random.uniform(-25, 25), random.uniform(-25, 25), random.uniform(0, 360)), (s, s, s * 0.7))

unreal.BlueprintEditorLibrary.compile_blueprint(bp); EAL.save_asset(BP_PATH, only_if_is_dirty=False)
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() == "VolumetricCloud":
        a.get_component_by_class(unreal.VolumetricCloudComponent).set_visibility(False); a.set_actor_hidden_in_game(True); log("default volumetric cloud hidden")
act = EAS.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0)); act.set_actor_label("CloudWorld")
log("components", len(act.get_components_by_class(unreal.StaticMeshComponent)))
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def trace(x, y):
    try:
        hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 500), unreal.Vector(x, y, -3000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if hit is None: return None
        t = hit.to_tuple(); return {"z": round(t[4].z, 1), "comp": t[10].get_name() if t[10] else None}
    except Exception as e: return "ERR " + repr(e)
for label, (x, y) in {"start": (0, 0), "step1": (360, 90), "step6": (2100, 20), "gap": (190, 48), "off": (0, 600)}.items():
    log("trace", label, trace(x, y))
with open(REPORT, "w", encoding="utf-8") as f: json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
print("V3 DONE errors=", len(rep["errors"]))
