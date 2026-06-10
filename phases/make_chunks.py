import json
import os

remaining_file = "C:/poligon/LLM_Traning/phases/remaining.txt"
with open(remaining_file, "r", encoding="utf-8") as f:
    files = [line.strip() for line in f if line.strip()]

chunk_size = 30
chunks = [files[i:i + chunk_size] for i in range(0, len(files), chunk_size)]

subagents = []
for idx, chunk in enumerate(chunks, 1):
    prompt_files = "\n".join(chunk)
    subagents.append({
        "TypeName": "translator",
        "Role": f"Translation improver {idx}",
        "Prompt": f"Please process these files:\n{prompt_files}",
        "Workspace": "inherit"
    })

output_file = "C:/poligon/LLM_Traning/phases/subagents_spec.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(subagents, f, indent=2, ensure_ascii=False)

print(f"Total files: {len(files)}")
print(f"Total chunks/subagents: {len(subagents)}")
