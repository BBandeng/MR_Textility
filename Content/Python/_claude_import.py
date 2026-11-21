import unreal, os, hashlib, glob, time
LOG=r'C:/Users/Bartl/Documents/GitHub/MR_Textility/Content/Python/_claude_log.txt'
SRC=r'C:/Users/Bartl/Documents/Unreal Projects/MyProject/Content/_ClaudeGLB'
MD5={'Angel1':'c7896a7d969d5e011ad322d289f09d7e','Angel2':'6c51c891ff57ca5c8cf0345a27e6525a','Angel3':'2992254466613ca15f69fc9086c4e105','Angel4':'8932bab45224228b2efa5ede3b280940','Dove1':'404e66e9ddc37b1761f8630640f21ae0','Dove2':'71d47e1734db33937ec546b7cc11bb24','Dove3':'60396287ac5c3c6f9b232833391cee04'}
O=[]
def log(): open(LOG,'w',encoding='utf-8').write(chr(10).join(O))
try:
    tasks=[]
    for n,h in MD5.items():
        out=os.path.join(SRC,n+'.glb')
        parts=sorted(glob.glob(os.path.join(SRC,n+'.glb.part*')))
        if not os.path.exists(out):
            with open(out,'wb') as f:
                for p in parts: f.write(open(p,'rb').read())
        d=hashlib.md5(open(out,'rb').read()).hexdigest()
        O.append(n+' parts='+str(len(parts))+' md5ok='+str(d==h))
        if d!=h: continue
        t=unreal.AssetImportTask()
        t.filename=out
        t.destination_path='/Game/Level1Heaven/Animated/'+n
        t.automated=True
        t.replace_existing=True
        t.save=True
        tasks.append(t)
    log()
    t0=time.time()
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    O.append('import secs=%.0f'%(time.time()-t0))
    for t in tasks:
        O.append('IMPORTED '+t.destination_path+' -> '+str(list(t.imported_object_paths)))
    for n in MD5:
        for a in unreal.EditorAssetLibrary.list_assets('/Game/Level1Heaven/Animated/'+n,True,False):
            ad=unreal.EditorAssetLibrary.find_asset_data(a)
            O.append('  A '+a+' cls='+str(ad.asset_class_path.asset_name))
except Exception as e:
    import traceback; O.append('ERR '+traceback.format_exc())
log()
