import json
import sys

with open("C:/poligon/LLM_Traning/phases/correct_batches.json", "r", encoding="utf-8") as f:
    batches = json.load(f)

batch_id = int(sys.argv[1])
for b in batches:
    if b["batch_id"] == batch_id:
        print("\n".join(b["files"]))
        break
