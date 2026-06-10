import json

with open("C:/poligon/LLM_Traning/phases/correct_batches.json", "r", encoding="utf-8") as f:
    batches = json.load(f)

registrations = {
    20: "f2bae5c8-d79a-4bba-9a73-c851d05896e5",
    21: "f7731947-05eb-4042-95f1-e7f4be52f07d"
}

for b in batches:
    bid = b["batch_id"]
    if bid in registrations:
        b["conversation_id"] = registrations[bid]
        b["status"] = "running"

with open("C:/poligon/LLM_Traning/phases/correct_batches.json", "w", encoding="utf-8") as f:
    json.dump(batches, f, indent=2, ensure_ascii=False)

print("Registered subagents for batch 20 and 21.")
