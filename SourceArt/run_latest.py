# Runs the most recently written job script in SourceArt/jobs
import glob, os, traceback
d = "C:/Users/Bartl/Desktop/MRPARADISE/SourceArt/jobs"
f = max(glob.glob(d + "/*.py"), key=os.path.getmtime)
print("RUNJOB", f)
try:
    exec(compile(open(f, encoding="utf-8").read(), f, "exec"), {"__name__": "__main__"})
except Exception:
    print("JOBERROR", traceback.format_exc())
