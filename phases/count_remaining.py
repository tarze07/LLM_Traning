import os

workspace = r"C:\poligon\LLM_Traning\phases"

def is_file_done(f):
    if f.endswith("_pl.md"):
        p1 = f[:-3] + "_pro.md"
        p2 = f[:-6] + "_pro.md"
        return os.path.exists(p1) or os.path.exists(p2)
    elif f.endswith("pl.md"):
        p1 = f[:-3] + "_pro.md"
        p2 = f[:-5] + "pro.md"
        return os.path.exists(p1) or os.path.exists(p2)
    else:
        p1 = f[:-3] + "_pro.md"
        return os.path.exists(p1)

pl_files = []
for root, dirs, files in os.walk(workspace):
    has_pro = any("pro.md" in f for f in files)
    if not has_pro:
        for f in files:
            if "pl.md" in f:
                pl_files.append(os.path.join(root, f))

remaining_files = [f for f in pl_files if not is_file_done(f)]

print(f"Total pl.md files: {len(pl_files)}")
print(f"Remaining files to process: {len(remaining_files)}")
for f in remaining_files[:10]:
    print(f)
