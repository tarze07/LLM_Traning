import os
import json

workspace = r"C:\poligon\LLM_Traning\phases"
batches_path = os.path.join(workspace, "correct_batches.json")

if not os.path.exists(batches_path):
    print("Error: correct_batches.json not found. Run prepare_batches.py first.")
    exit(1)

with open(batches_path, "r", encoding="utf-8") as f:
    batches = json.load(f)

completed_count = 0
running_count = 0
pending_count = 0

def is_file_done(f):
    if f.endswith("_pl.md"):
        p1 = f[:-3] + "_pro.md"   # README_pl_pro.md
        p2 = f[:-6] + "_pro.md"   # README_pro.md
        return os.path.exists(p1) or os.path.exists(p2)
    elif f.endswith("pl.md"):
        p1 = f[:-3] + "_pro.md"   # pl_pro.md
        p2 = f[:-5] + "pro.md"    # pro.md
        return os.path.exists(p1) or os.path.exists(p2)
    else:
        p1 = f[:-3] + "_pro.md"
        return os.path.exists(p1)

for batch in batches:
    all_done = True
    done_count = 0
    for f in batch["files"]:
        if is_file_done(f):
            done_count += 1
        else:
            all_done = False
            
    if all_done:
        batch["status"] = "completed"
        completed_count += 1
    elif done_count > 0:
        batch["status"] = "running"
        running_count += 1
    else:
        batch["status"] = "pending"
        pending_count += 1

with open(batches_path, "w", encoding="utf-8") as f:
    json.dump(batches, f, indent=2, ensure_ascii=False)

print(f"Status: {completed_count} completed, {running_count} running, {pending_count} pending out of {len(batches)} batches.")

# Output the next 3 pending batches for easy copy-paste/invocation
pending_batches = [b for b in batches if b["status"] == "pending"]
if pending_batches:
    print("\nNext pending batches:")
    for b in pending_batches[:3]:
        print(f"\n--- Batch {b['batch_id']} ---")
        print("\n".join(b["files"]))
else:
    print("\nAll batches completed!")
