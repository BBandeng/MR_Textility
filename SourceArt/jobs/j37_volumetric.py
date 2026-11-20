# v6: UE volumetric clouds everywhere, angels in a ring round the sun, oil-paint post, collage shards.
import unreal, json, math, random, os
REPORT = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/job_report.json"
BACKUP = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/angel_transforms_backup.json"
rep = {"steps": [], "errors": []}
def log(*a):
    s = " ".join(str(x) for x in a); rep["steps"].append(s); print("V6", s)
def err(*a):
    s = " ".join(str(x) for x in a); rep["errors"].append(s); print("V6 ERROR", s)
def setp(o, n, v):
    try: o.set_editor_property(n, v)
    except Exception as e: err("setprop", n, repr(e))
AT = unreal.AssetToolsHelpers.get_asset_tools(); MEL = unreal.MaterialEditingLibrary; EAL = unreal.EditorAssetLibrary
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
SDL = unreal.SubobjectDataBlueprintFunctionLibrary; sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
ML = unreal.MathLibrary
DEST = "/Game/PaintClouds"
random.seed(77)

# ---------------------------------------------------------------- volumetric cloud + sky
vp = f"{DEST}/MI_VolCloud"
mi_vol = unreal.load_asset(vp) if EAL.does_asset_exist(vp) else AT.create_asset("MI_VolCloud", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
parent = unreal.load_asset("/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst")
MEL.set_material_instance_parent(mi_vol, parent)
for n in MEL.get_scalar_parameter_names(parent):
    log("vol scalar", n, MEL.get_material_instance_scalar_parameter_value(parent, n))
MEL.update_material_instance(mi_vol); EAL.save_asset(vp, only_if_is_dirty=False)
for a in EAS.get_all_level_actors():
    cls = a.get_class().get_name()
    if cls == "SkyAtmosphere":
        a.set_actor_location(unreal.Vector(0, 0, -300000.0), False, False); log("atmosphere ground z=-3km")
    elif cls == "VolumetricCloud":
        c = a.get_component_by_class(unreal.VolumetricCloudComponent)
        log("cloud before", c.get_editor_property("layer_bottom_altitude"), c.get_editor_property("layer_height"), c.get_editor_property("material").get_path_name() if c.get_editor_property("material") else None)
        setp(c, "material", mi_vol)
        setp(c, "layer_bottom_altitude", 1.5); setp(c, "layer_height", 4.0)
        c.set_visibility(True); a.set_actor_hidden_in_game(False)

# ---------------------------------------------------------------- angels in a ring round the sun
angels = []
for a in EAS.get_all_level_actors():
    if a.get_class().get_name() != "StaticMeshActor": continue
    c = a.get_component_by_class(unreal.StaticMeshComponent)
    if c and c.static_mesh and "/Game/Layer1/Layer1_NoSun/" in c.static_mesh.get_path_name() and "Canopy" not in c.static_mesh.get_name():
        angels.append(a)
log("angels", len(angels))
if not os.path.exists(BACKUP):
    bk = {}
    for a in angels:
        l = a.get_actor_location(); r = a.get_actor_rotation()
        bk[a.get_actor_label()] = [l.x, l.y, l.z, r.roll, r.pitch, r.yaw]
    json.dump(bk, open(BACKUP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
else:
    bk = json.load(open(BACKUP, encoding="utf-8"))
    for a in angels:                       # always start from the original pose
        v = bk.get(a.get_actor_label())
        if v:
            a.set_actor_location(unreal.Vector(v[0], v[1], v[2]), False, False)
            a.set_actor_rotation(unreal.Rotator(roll=v[3], pitch=v[4], yaw=v[5]), False)
RING_R, RING_Z = 11000.0, 16000.0
order = sorted(angels, key=lambda a: math.atan2(a.get_actor_location().y, a.get_actor_location().x))
ring_pos = []
for i, a in enumerate(order):
    l = a.get_actor_location()
    old = math.degrees(math.atan2(l.y, l.x)); new = -180.0 + 360.0 * (i + 0.5) / len(order)
    d = new - old
    rr = RING_R * (1.0 if i % 2 == 0 else 0.82); zz = RING_Z + (0 if i % 2 == 0 else 2500)
    p = unreal.Vector(rr * math.cos(math.radians(new)), rr * math.sin(math.radians(new)), zz)
    a.set_actor_rotation(ML.compose_rotators(a.get_actor_rotation(), unreal.Rotator(roll=0, pitch=0, yaw=d)), False)
    a.set_actor_location(p, False, False)
    ring_pos.append((p.x, p.y, p.z))
log("ring placed", len(ring_pos))

# ---------------------------------------------------------------- shard textures + materials
tasks = []
for k in range(1, 5):
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", f"C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/shard_sprites/T_Shard_{k}.png")
    t.set_editor_property("destination_path", DEST + "/Shards")
    t.set_editor_property("automated", True); t.set_editor_property("replace_existing", True); t.set_editor_property("save", True)
    tasks.append(t)
AT.import_asset_tasks(tasks)
card = unreal.load_asset(f"{DEST}/M_CloudCard")
shard_mis = []
for k in range(1, 5):
    t = unreal.load_asset(f"{DEST}/Shards/T_Shard_{k}")
    if not t: err("shard texture missing", k); continue
    p = f"{DEST}/MI_Shard_{k}"
    mi = unreal.load_asset(p) if EAL.does_asset_exist(p) else AT.create_asset(f"MI_Shard_{k}", DEST, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, card); MEL.set_material_instance_texture_parameter_value(mi, "Cloud", t)
    MEL.update_material_instance(mi); EAL.save_asset(p, only_if_is_dirty=False); shard_mis.append(mi)

# ---------------------------------------------------------------- blueprint
mi_puff = unreal.load_asset(f"{DEST}/MI_PaintCloud")
clouds = []; bowl = None
for p in EAL.list_assets(DEST, recursive=True):
    a = unreal.load_asset(p.split(".")[0])
    if isinstance(a, unreal.StaticMesh):
        if a.get_name().startswith("PaintCloud_"): clouds.append(a)
        elif a.get_name() == "AbyssBowl": bowl = a
cz = {m.get_name(): m.get_bounding_box().max.z for m in clouds}
plane = unreal.load_asset("/Engine/BasicShapes/Plane"); cyl = unreal.load_asset("/Engine/BasicShapes/Cylinder")
mi_inv = unreal.load_asset("/Game/Layer1/Materials/MI_Cloud_Invisible")
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

add_mesh("Abyss", bowl, unreal.load_asset(f"{DEST}/M_Abyss"), (0, 0, 0), R(), (15000, 15000, 15000))
STEPS = [(0, 0, 0, 170), (360, 90, 15, 130), (700, -60, 35, 140), (1040, 120, 20, 125), (1400, 30, 45, 150),
         (1750, -150, 30, 130), (2100, 20, 55, 140), (-330, -150, -15, 130), (-640, 60, -30, 135)]
for i, (x, y, z, r) in enumerate(STEPS):
    add_mesh(f"Step{i}_Collision", cyl, mi_inv, (x, y, z - 15), R(), (r / 50.0, r / 50.0, 0.3), collide=True)
    mesh = random.choice(clouds); k = r / 100.0 * 1.35; kz = k * 0.45
    add_mesh(f"Step{i}_Cloud", mesh, mi_puff, (x, y, z + 12 - cz[mesh.get_name()] * kz), R(yaw=random.uniform(0, 360)), (k, k, kz))

TARGET = (0.0, 0.0, 170.0)
def face_rot(loc):
    d = [TARGET[i] - loc[i] for i in range(3)]; n = math.sqrt(sum(v * v for v in d)) or 1.0
    z = [d[0] / n + random.uniform(-0.35, 0.35), d[1] / n + random.uniform(-0.35, 0.35), d[2] / n + random.uniform(-0.2, 0.2)]
    n = math.sqrt(sum(v * v for v in z)); z = [v / n for v in z]
    a = random.uniform(0, 2 * math.pi)
    return ML.make_rot_from_zx(unreal.Vector(*z), unreal.Vector(math.cos(a), math.sin(a), 0.0))
ns = 0
if shard_mis:
    for (px, py, pz) in ring_pos:
        for j in range(5):
            loc = (px + random.uniform(-3500, 3500), py + random.uniform(-3500, 3500), pz + random.uniform(-3000, 3000))
            w = random.uniform(4, 13)
            add_mesh(f"Shard_{ns}", plane, random.choice(shard_mis), loc, face_rot(loc), (w, w, 1.0)); ns += 1
    for j in range(14):          # loose flecks drifting toward the sun
        a = random.uniform(0, 2 * math.pi); d = random.uniform(1500, 8000)
        loc = (math.cos(a) * d, math.sin(a) * d, random.uniform(17000, 24000)); w = random.uniform(2, 7)
        add_mesh(f"Shard_{ns}", plane, random.choice(shard_mis), loc, face_rot(loc), (w, w, 1.0)); ns += 1
log("shards", ns)

pp = add(unreal.PostProcessComponent, "OilPaintPost")
if pp:
    setp(pp, "unbound", True)
    st = pp.get_editor_property("settings"); wb = unreal.WeightedBlendables()
    b = unreal.WeightedBlendable(); b.set_editor_property("weight", 1.0); b.set_editor_property("object", unreal.load_asset("/Game/GoldenSky/M_OilPaint"))
    wb.set_editor_property("array", [b]); st.set_editor_property("weighted_blendables", wb); setp(pp, "settings", st)

unreal.BlueprintEditorLibrary.compile_blueprint(bp); EAL.save_asset(BP_PATH, only_if_is_dirty=False)
act = EAS.spawn_actor_from_class(bp.generated_class(), unreal.Vector(0, 0, 0)); act.set_actor_label("CloudWorld")
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(0, 0, 170), unreal.Rotator(roll=0, pitch=62, yaw=0))
with open(REPORT, "w", encoding="utf-8") as f: json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
print("V6 DONE errors=", len(rep["errors"]))
