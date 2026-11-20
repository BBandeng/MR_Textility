# BP_CloudWorld: keep the flat sky layers, replace everything lower with Cloud Forge VDB clouds in clumps.
import unreal, json, math, random
REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("VDB", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("VDB ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary; sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
random.seed(91)
CF = "/Game/Cloud_Forge_VDB_Vol3"
base_mat = unreal.load_asset(f"{CF}/VDB_Materials/VDB_Single_Material/M_VDB_Cloud_Single")
KITS = ["01", "04", "05", "06", "07", "10", "13", "14", "18", "19"]
kits = []
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for k in KITS:
    svt = unreal.load_asset(f"{CF}/VDB_Collection/VDB_AP_Cumulus_Cloud/Kit_cumulus_{k}")
    if not svt: err("kit missing", k); continue
    p = f"/Game/PaintClouds/VDB/MI_Cumulus_{k}"
    mi = unreal.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(f"MI_Cumulus_{k}", "/Game/PaintClouds/VDB", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, base_mat)
    MEL.set_material_instance_sparse_volume_texture_parameter_value(mi, "VDB_Texture", svt)
    MEL.set_material_instance_scalar_parameter_value(mi, "Density_Multiplier", 1.0)
    MEL.update_material_instance(mi); EAL.save_asset(p, only_if_is_dirty=False)
    # measure native size with a temporary actor
    ext = None
    try:
        tmp = EAS.spawn_actor_from_class(unreal.HeterogeneousVolume, unreal.Vector(0, 0, 500000))
        c = tmp.get_component_by_class(unreal.HeterogeneousVolumeComponent)
        c.set_material(0, mi)
        o, e = tmp.get_actor_bounds(False)
        ext = (e.x, e.y, e.z); EAS.destroy_actor(tmp)
    except Exception as ex:
        err("measure", k, repr(ex))
    kits.append((mi, ext))
    log("kit", k, ext)

canopy = unreal.load_asset("/Game/Layer1/Layer1_NoSun/StaticMeshes/Canopy___Continuous_mesh___80k_002")
mi_layer = unreal.load_asset("/Game/Layer1/Materials/MI_Cloud_BlenderLook")
mi_inv = unreal.load_asset("/Game/Layer1/Materials/MI_Cloud_Invisible")
cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder")
zmin = canopy.get_bounding_box().min.z

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
def add(cls, name):
    h, why = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=cls, blueprint_context=bp))
    if not SDL.is_handle_valid(h): err("add failed", name, str(why)); return None
    sds.rename_subobject(h, unreal.Text(name)); return SDL.get_object(SDL.get_data(h))
def add_mesh(name, mesh, mat, loc, rot, scale, collide=False):
    c = add(unreal.StaticMeshComponent, name)
    if not c: return
    setp(c, "static_mesh", mesh); setp(c, "override_materials", [mat])
    setp(c, "relative_location", unreal.Vector(*loc)); setp(c, "relative_rotation", rot); setp(c, "relative_scale3d", unreal.Vector(*scale))
    setp(c, "cast_shadow", False)
    try: c.set_collision_profile_name("BlockAll" if collide else "NoCollision")
    except Exception as e: err("collision", name, repr(e))
    if collide: setp(c, "hidden_in_game", True)
nv = [0]
def add_vdb(name, loc, width, top_at=None):
    """width = target horizontal size in cm. top_at: place so the cloud top sits at this z."""
    mi, ext = random.choice(kits)
    c = add(unreal.HeterogeneousVolumeComponent, name)
    if not c: return
    native = max(ext[0], ext[1]) * 2 if ext and max(ext[0], ext[1]) > 1 else 100.0
    s = width / native
    z = loc[2]
    if top_at is not None and ext: z = top_at - ext[2] * s * 0.55
    setp(c, "override_materials", [mi])
    setp(c, "relative_location", unreal.Vector(loc[0], loc[1], z)); setp(c, "relative_rotation", R(yaw=random.uniform(0, 360)))
    setp(c, "relative_scale3d", unreal.Vector(s, s, s))
    nv[0] += 1

# --- sky layers: unchanged from the flat version
for n, sxy, sz, bottom, yaw, roll, pitch, off in [("Sky_Low", 170, 70, 3500, 0, 6, 0, (0, 0)),
        ("Sky_Mid", 260, 80, 11000, 75, 0, -4, (-3000, 2000)), ("Sky_High", 380, 90, 20000, 160, 3, 3, (2500, -3500))]:
    add_mesh(n, canopy, mi_layer, (off[0], off[1], bottom - zmin * sz), R(roll, pitch, yaw), (sxy, sxy, sz))

# --- clouds under the feet (same five spots as before), walkable via hidden colliders
PLATFORMS = [(0, 0, 0, 700), (1300, 300, 40, 500), (2300, -300, 80, 450), (3300, 200, 40, 600), (-1200, -600, -30, 450)]
for i, (x, y, z, r) in enumerate(PLATFORMS):
    add_mesh(f"Step{i}_Collision", cyl, mi_inv, (x, y, z - 25), R(), (r / 50.0, r / 50.0, 0.5), collide=True)
    add_vdb(f"Step{i}_Cloud", (x, y, z), r * 3.0, top_at=z + 60)

# --- clumps of clouds around the character
def clump(prefix, centre, count, spread, wmin, wmax, zjit):
    for j in range(count):
        a = random.uniform(0, 2 * math.pi); d = spread * math.sqrt(random.random())
        add_vdb(f"{prefix}_{j}", (centre[0] + math.cos(a) * d, centre[1] + math.sin(a) * d, centre[2] + random.uniform(-zjit, zjit)), random.uniform(wmin, wmax))
for i in range(6):
    a = 2 * math.pi * (i + random.uniform(-0.3, 0.3)) / 6; d = random.uniform(2500, 6500)
    clump(f"Around{i}", (1000 + math.cos(a) * d, math.sin(a) * d, random.uniform(-600, 1800)), 3, 1800, 1500, 4000, 500)
# --- layer just below the feet
for i in range(5):
    a = random.uniform(0, 2 * math.pi); d = random.uniform(1500, 12000)
    clump(f"BelowNear{i}", (1000 + math.cos(a) * d, math.sin(a) * d, random.uniform(-5500, -2800)), 3, 4000, 4000, 9000, 900)
# --- deep layer
for i in range(4):
    a = random.uniform(0, 2 * math.pi); d = random.uniform(3000, 40000)
    clump(f"BelowFar{i}", (math.cos(a) * d, math.sin(a) * d, random.uniform(-22000, -12000)), 3, 14000, 12000, 26000, 3000)

unreal.BlueprintEditorLibrary.compile_blueprint(bp); EAL.save_asset(BP_PATH, only_if_is_dirty=False)
act = EAS.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0)); act.set_actor_label("CloudWorld")
log("vdb clouds", nv[0])
def trace(x, y):
    try:
        hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 500), unreal.Vector(x, y, -3000), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if hit is None: return None
        t = hit.to_tuple(); return {"z": round(t[4].z, 1), "comp": t[10].get_name() if t[10] else None}
    except Exception as e: return "ERR " + repr(e)
for label, (x, y) in {"start": (0, 0), "step1": (1300, 300), "off": (0, 1500)}.items(): log("trace", label, trace(x, y))
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(-300, -100, 175), unreal.Rotator(roll=0, pitch=-6, yaw=10))
json.dump(rep, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("VDB DONE errors=", len(rep["errors"]))
