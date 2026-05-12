import re
import random

def analyze_log():
    log_path = "verify_log.txt"
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(log_path, "r", encoding="utf-16") as f:
            lines = f.readlines()
    
    debug_lines = [line.strip() for line in lines if "DEBUG_1A_CHECK" in line]
    
    targets = ["Base.Hammer", "Base.Screwdriver", "Base.TinOpener"]
    found_targets = {t: [] for t in targets}
    
    print(f"Total DEBUG_1A_CHECK lines: {len(debug_lines)}")
    
    for line in debug_lines:
        for t in targets:
            if f": {t} |" in line:
                found_targets[t].append(line)
    
    print("\n=== Representative Items Check ===")
    for t in targets:
        if found_targets[t]:
            print(f"[{t}] Found matches:")
            for l in found_targets[t]:
                print(f"  {l}")
        else:
            print(f"[{t}] NO MATCHES found in 1-A logic (Correct for TinOpener, Bad for Hammer/Screwdriver)")

    print("\n=== Random Sample (20 items) ===")
    if debug_lines:
        sample = random.sample(debug_lines, min(20, len(debug_lines)))
        for l in sample:
            print(l)
    else:
        print("No debug lines found.")

if __name__ == "__main__":
    analyze_log()
