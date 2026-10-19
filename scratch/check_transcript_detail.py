import json

path = r"C:\Users\Chris Williams\.gemini\antigravity\brain\fddc0bb3-e31c-4290-9542-89fe3f0dd2f4\.system_generated\logs\transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    try:
        obj = json.loads(line)
        idx = obj.get("step_index", 0)
        if idx >= 24614:
            src = obj.get("source")
            typ = obj.get("type")
            tool_calls = obj.get("tool_calls", [])
            content = str(obj.get("content", ""))[:200]
            print(f"[{idx}] {src} - {typ} - tools:{[tc['name'] for tc in tool_calls] if tool_calls else ''} - {content}")
    except Exception:
        pass
