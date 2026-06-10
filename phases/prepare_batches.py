import os
import json

workspace = r"C:\poligon\LLM_Traning\phases"

pl_files = []
for root, dirs, files in os.walk(workspace):
    # Check if there is any file containing 'pro.md' in this directory
    has_pro = any("pro.md" in f for f in files)
    if not has_pro:
        for f in files:
            if "pl.md" in f:
                pl_files.append(os.path.join(root, f))

# Sort to have a deterministic order
pl_files.sort()

# Save the remaining files list
with open(os.path.join(workspace, "correct_remaining.txt"), "w", encoding="utf-8") as f:
    for pf in pl_files:
        f.write(pf + "\n")

# Create batches of 25 files
chunk_size = 25
batches = []
for i in range(0, len(pl_files), chunk_size):
    chunk = pl_files[i:i+chunk_size]
    batches.append({
        "batch_id": (i // chunk_size) + 1,
        "files": chunk,
        "status": "pending",
        "conversation_id": None
    })

with open(os.path.join(workspace, "correct_batches.json"), "w", encoding="utf-8") as f:
    json.dump(batches, f, indent=2, ensure_ascii=False)

print(f"Total files: {len(pl_files)}")
print(f"Total batches: {len(batches)}")
