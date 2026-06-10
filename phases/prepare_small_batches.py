import os
import json

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

# Sort to be deterministic
pl_files.sort()

remaining_files = [f for f in pl_files if not is_file_done(f)]

# Split into batches of 15
chunk_size = 15
batches = []
for i in range(0, len(remaining_files), chunk_size):
    chunk = remaining_files[i:i+chunk_size]
    batches.append({
        "batch_id": (i // chunk_size) + 1,
        "files": chunk,
        "status": "pending",
        "conversation_id": None
    })

with open(os.path.join(workspace, "correct_batches.json"), "w", encoding="utf-8") as f:
    json.dump(batches, f, indent=2, ensure_ascii=False)

print(f"Total remaining files: {len(remaining_files)}")
print(f"Total new small batches generated: {len(batches)}")
