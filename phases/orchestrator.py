import os
import json
import sys

STATE_FILE = "C:/poligon/LLM_Traning/phases/state.json"
REMAINING_FILE = "C:/poligon/LLM_Traning/phases/remaining.txt"
CHUNK_SIZE = 30
MAX_CONCURRENT = 3

def get_pro_path(pl_path):
    pl_path = pl_path.lstrip("\ufeff")
    return pl_path.replace(".md", "_pro.md")

def init_state():
    if not os.path.exists(REMAINING_FILE):
        print(f"Error: {REMAINING_FILE} not found.")
        sys.exit(1)
        
    with open(REMAINING_FILE, "r", encoding="utf-8") as f:
        files = [line.strip() for line in f if line.strip()]
        
    batches = []
    for i in range(0, len(files), CHUNK_SIZE):
        chunk = files[i:i+CHUNK_SIZE]
        batches.append({
            "id": len(batches) + 1,
            "files": chunk,
            "status": "pending",
            "conversation_id": None
        })
        
    state = {"batches": batches}
    save_state(state)
    print(f"Initialized state with {len(batches)} batches.")
    return state

def load_state():
    if not os.path.exists(STATE_FILE):
        return init_state()
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading state: {e}. Re-initializing.")
        return init_state()

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def update_state(state):
    changed = False
    for batch in state["batches"]:
        # Verify batch files status from filesystem
        all_done = True
        done_count = 0
        for f in batch["files"]:
            pro_f = get_pro_path(f)
            if os.path.exists(pro_f):
                done_count += 1
            else:
                all_done = False
                
        if all_done:
            if batch["status"] != "completed":
                batch["status"] = "completed"
                changed = True
        elif done_count > 0:
            # If some are done, but not all, it's still running or needs to be resumed
            if batch["status"] == "pending":
                batch["status"] = "running"
                changed = True
        else:
            # None done
            if batch["status"] == "completed":
                batch["status"] = "pending"
                changed = True
                
    if changed:
        save_state(state)

def get_status_summary(state):
    pending = sum(1 for b in state["batches"] if b["status"] == "pending")
    running = sum(1 for b in state["batches"] if b["status"] == "running")
    completed = sum(1 for b in state["batches"] if b["status"] == "completed")
    return f"Status: {completed} completed, {running} running, {pending} pending out of {len(state['batches'])} batches."

def main():
    state = load_state()
    update_state(state)
    
    # Handle registration
    if len(sys.argv) > 1 and sys.argv[1] == "register":
        if len(sys.argv) < 4:
            print("Usage: orchestrator.py register <batch_id> <conversation_id>")
            sys.exit(1)
        batch_id = int(sys.argv[2])
        conv_id = sys.argv[3]
        for batch in state["batches"]:
            if batch["id"] == batch_id:
                batch["conversation_id"] = conv_id
                batch["status"] = "running"
                save_state(state)
                print(f"Registered batch {batch_id} with conversation ID {conv_id}.")
                return
        print(f"Error: Batch {batch_id} not found.")
        sys.exit(1)
        
    if len(sys.argv) > 1 and sys.argv[1] == "reset_running":
        for batch in state["batches"]:
            if batch["status"] == "running":
                batch["status"] = "pending"
                batch["conversation_id"] = None
        save_state(state)
        print("Reset all running batches back to pending.")
        return

    # Count currently running batches
    running_batches = [b for b in state["batches"] if b["status"] == "running"]
    active_count = len(running_batches)
    
    print(get_status_summary(state))
    
    # Check if we need to spawn more
    spawns_needed = MAX_CONCURRENT - active_count
    next_to_spawn = []
    
    if spawns_needed > 0:
        for batch in state["batches"]:
            if batch["status"] == "pending":
                next_to_spawn.append(batch)
                if len(next_to_spawn) == spawns_needed:
                    break
                    
    # Generate action output
    actions = []
    for batch in next_to_spawn:
        cleaned_files = [f.lstrip("\ufeff") for f in batch["files"]]
        prompt_files = "\n".join(cleaned_files)
        actions.append({
            "batch_id": batch["id"],
            "TypeName": "translator",
            "Role": f"Translation improver {batch['id']}",
            "Prompt": f"Please process these files:\n{prompt_files}",
            "Workspace": "inherit"
        })
        
    with open("C:/poligon/LLM_Traning/phases/next_actions.json", "w", encoding="utf-8") as f:
        json.dump(actions, f, indent=2, ensure_ascii=False)
        
    if actions:
        print(f"Generated next actions for {len(actions)} batches in next_actions.json.")
    else:
        print("No new actions generated (either at max concurrency or all batches are complete).")

if __name__ == "__main__":
    main()
