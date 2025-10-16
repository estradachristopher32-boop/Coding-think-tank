"""
Small runner that can execute a plan of "needs" (scripted steps).
"""
import os, subprocess, time

def ask(prompt: str) -> bool:
    ans = input(f"{prompt} [y/N]: ").strip().lower()
    return ans in ("y","yes")

def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def run_cmd(cmd: str, cwd: str = None):
    subprocess.run(cmd, shell=True, check=False, cwd=cwd)

def run_plan(plan):
    for i, step in enumerate(plan.get("steps", []), 1):
        name = step.get("name", f"step-{i}")
        print(f"\n== {i}. {name} ==")
        for f in step.get("files", []):
            if ask(f"Create/overwrite file '{f['path']}'?"):
                write_file(f["path"], f["content"])
        for c in step.get("cmd", []):
            if ask(f"Run command?\n{c}"):
                run_cmd(c, cwd=step.get("cwd"))
        wait = step.get("wait_sec", 0)
        if wait:
            print(f"…waiting {wait}s"); time.sleep(wait)
    print("\n✔ Plan complete.")
