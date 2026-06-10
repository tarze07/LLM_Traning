import json

with open("C:/poligon/LLM_Traning/phases/correct_batches.json", "r", encoding="utf-8") as f:
    batches = json.load(f)

pending_batches = [b for b in batches if b["status"] == "pending"]

subagents_args = []
for b in pending_batches[:2]: # 2 BATCHES AT A TIME IS A GOOD BALANCE
    files_str = "\n".join(b["files"])
    subagents_args.append({
        "TypeName": "translator",
        "Role": f"Translation improver {b['batch_id']}",
        "Prompt": f"Please process these files:\n{files_str}",
        "Workspace": "inherit"
    })

with open("C:/poligon/LLM_Traning/phases/next_tool_call.json", "w", encoding="utf-8") as f:
    json.dump(subagents_args, f, indent=2, ensure_ascii=False)

print("Generated next_tool_call.json with 2 batches")
