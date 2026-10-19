import json

path = r"C:\Users\Chris Williams\.gemini\antigravity\brain\fddc0bb3-e31c-4290-9542-89fe3f0dd2f4\.system_generated\logs\transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
user_msgs = []
for line in lines:
    if '"USER_INPUT"' in line:
        try:
            obj = json.loads(line)
            user_msgs.append((obj.get("step_index"), obj.get("content")))
        except Exception:
            pass

print("Last 10 user inputs:")
for idx, content in user_msgs[-10:]:
    print(f"[{idx}]: {content}")
