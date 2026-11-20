# Builds BP_CloudWorld: layered flat clouds above, walkable cloud platforms,
# wisps at body height, non-walkable layers below. Removes the grid floor.
import unreal, json, math, random

REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("CW", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("CW ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))

AT = unreal.AssetToolsHelpers.get_asset_tools()
MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)

def s2l(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

# ---------------------------------------------------------------- materials
MPKG = "/Game/Layer1/Materials"
master = unreal.load_asset(f"{MPKG}/M_Cloud_BlenderLook")
def make_mi(name, rgb, opacity):
    p = f"{MPKG}/{name}"
    mi = unreal.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(
        name, MPKG, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, master)
    MEL.set_material_instance_vector_parameter_value(mi, "CloudColor", unreal.LinearColor(s2l(rgb[0]), s2l(rgb[1]), s2l(rgb[2]), 1.0))
    MEL.set_material_instance_scalar_parameter_value(mi, "Opacity", opacity)
    MEL.update_material_instance(mi)
    EAL.save_asset(p, only_if_is_dirty=False)
    return mi
mi_layer = unreal.load_asset(f"{MPKG}/MI_Cloud_BlenderLook")
mi_walk = make_mi("MI_Cloud_Walkable", (236, 230, 218), 0.92)
mi_wisp = make_mi("MI_Cloud_Wisp", (205, 210, 216), 0.28)

canopy = unreal.load_asset("/Game/Layer1/Layer1_NoSun/StaticMeshes/Canopy___Continuous_mesh___80k_002")
sphere = unreal.load_asset("/Engine/BasicShapes/Sphere")
cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder")
bb = canopy.get_bounding_box()
log("canopy bbox", bb.min, bb.max)
zmin, zmax = bb.min.z, bb.max.z

# ---------------------------------------------------------------- blueprint
BPKG = "/Game/Layer1/Blueprints"
BP_PATH = f"{BPKG}/BP_CloudWorld"
if EAL.does_asset_exist(BP_PATH):
    old = unreal.load_asset(BP_PATH)
    for a in list(EAS.get_all_level_actors()):
        if a.get_class() == old.generated_class():
            EAS.destroy_actor(a)
    EAL.delete_asset(BP_PATH)
fac = unreal.BlueprintFactory(); fac.set_editor_property("parent_class", unreal.Actor)
bp = AT.create_asset("BP_CloudWorld", BPKG, unreal.Blueprint, fac)
root = sds.k2_gather_subobject_data_for_blueprint(bp)[0]

def add_mesh(name, mesh, mat, loc, rot, scale, collide=False, hidden=False):
    h, why = sds.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=root, new_class=unreal.StaticMeshComponent, blueprint_context=bp))
    if not SDL.is_handle_valid(h):
        err("add failed", name, str(why)); return
    sds.rename_subobject(h, unreal.Text(name))
    c = SDL.get_object(SDL.get_data(h))
    setp(c, "static_mesh", mesh)
    if mat: setp(c, "override_materials", [mat])
    setp(c, "relative_location", unreal.Vector(*loc))
    setp(c, "relative_rotation", unreal.Rotator(roll=rot[0], pitch=rot[1], yaw=rot[2]))
    setp(c, "relative_scale3d", unreal.Vector(*scale))
    setp(c, "cast_shadow", False)
    try: c.set_collision_profile_name("BlockAll" if collide else "NoCollision")
    except Exception as e: err("collision", name, repr(e))
    if hidden:
        setp(c, "visible", False); setp(c, "hidden_in_game", True)

# --- cloud layers above (bottom height in cm) and below (top height in cm)
#        name        sxy  sz  height   yaw  roll pitch  offset xy
UPPER = [("Sky_Low",  170, 70,  3500,    0,   6,  0, (0, 0)),
         ("Sky_Mid",  260, 80, 11000,   75,   0, -4, (-3000, 2000)),
         ("Sky_High", 380, 90, 20000,  160,   3,  3, (2500, -3500))]
for n, sxy, sz, bottom, yaw, roll, pitch, off in UPPER:
    add_mesh(n, canopy, mi_layer, (off[0], off[1], bottom - zmin * sz), (roll, pitch, yaw), (sxy, sxy, sz))
LOWER = [("Below_Near", 200, 60, -1500,  40,  0, -5, (6000, 3000)),
         ("Below_Far",  420, 90, -9000, 120,  0,  0, (-8000, -5000))]
for n, sxy, sz, top, yaw, roll, pitch, off in LOWER:
    add_mesh(n, canopy, mi_layer, (off[0], off[1], top - zmax * sz), (roll, pitch, yaw), (sxy, sxy, sz))

# --- walkable cloud platforms: (x, y, top z, radius) in cm
PLATFORMS = [(0, 0, 0, 700), (1300, 300, 40, 500), (2300, -300, 80, 450),
             (3300, 200, 40, 600), (-1200, -600, -30, 450)]
random.seed(7)
for i, (x, y, z, r) in enumerate(PLATFORMS):
    add_mesh(f"Step{i}_Collision", cyl, None, (x, y, z - 25), (0, 0, 0), (r / 50.0, r / 50.0, 0.5), collide=True, hidden=True)
    k = r / 50.0
    add_mesh(f"Step{i}_Cloud", sphere, mi_walk, (x, y, z + 10 - 80), (0, 0, 0), (k, k, 1.6))
    for j in range(3):
        ang = math.radians(120 * j + random.uniform(-25, 25))
        sz = random.uniform(2.0, 2.6)
        add_mesh(f"Step{i}_Lobe{j}", sphere, mi_walk,
                 (x + math.cos(ang) * r * 0.45, y + math.sin(ang) * r * 0.45, z + 5 - 50 * sz),
                 (0, 0, math.degrees(ang)), (k * 0.62, k * 0.5, sz))
    # wisps drifting at body height around the platform (walk-through)
    for j in range(3):
        ang = math.radians(random.uniform(0, 360))
        d = r * random.uniform(0.55, 1.25)
        add_mesh(f"Step{i}_Wisp{j}", sphere, mi_wisp,
                 (x + math.cos(ang) * d, y + math.sin(ang) * d, z + random.uniform(40, 230)),
                 (0, 0, random.uniform(0, 180)),
                 (random.uniform(5, 9), random.uniform(3.5, 6), random.uniform(1.2, 2.6)))

unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_asset(BP_PATH, only_if_is_dirty=False)
log("blueprint ok", BP_PATH)

# ---------------------------------------------------------------- level
for a in EAS.get_all_level_actors():
    if a.get_actor_label() == "Floor":
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        c.set_visibility(False); a.set_actor_hidden_in_game(True)
        c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        log("Floor hidden, collision off")
    elif a.get_class().get_name() == "StaticMeshActor":
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh and "Canopy" in c.static_mesh.get_name():
            c.set_visibility(False); a.set_actor_hidden_in_game(True)
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            log("original canopy hidden", a.get_actor_label())

act = EAS.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0))
act.set_actor_label("CloudWorld")
log("spawned CloudWorld, components", len(act.get_components_by_class(unreal.StaticMeshComponent)))

# ---------------------------------------------------------------- collision check
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
def trace(x, y):
    try:
        hit = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 500), unreal.Vector(x, y, -3000),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if hit is None: return None
        t = hit.to_tuple()
        return {"blocking": t[0], "z": round(t[4].z, 1), "comp": t[10].get_name() if t[10] else None}
    except Exception as e:
        return "ERR " + repr(e)
for label, (x, y) in {"start": (0, 0), "step1": (1300, 300), "step3": (3300, 200), "gap_0_1": (760, 180), "off_cloud": (0, 1500), "far": (6000, 6000)}.items():
    log("trace", label, trace(x, y))

unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(
    unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=60, yaw=0))
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
print("CW DONE errors=", len(rep["errors"]))
