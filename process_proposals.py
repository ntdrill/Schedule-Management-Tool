import os
import re
from typing import List, Dict, Any

# --- Configuration ---
DATA_DIR = "data"
PROPOSALS_DIR = "Agent_workspace/Task_Management/01_Proposals"
OUTPUT_DIR = "data" # Overwrite

# Symbol Generators
def char_range(start_code, count):
    return [chr(start_code + i) for i in range(count)]

SYMBOLS = {
    "Group A": char_range(0x1401, 100), # Canadian Aboriginal Syllabics (Physical Constants)
    "Group B": char_range(0x1200, 100), # Ethiopic (System Settings)
    "Group C": char_range(0xA000, 100), # Yi Syllables (Dynamic State)
    "Group D": char_range(0x2500, 50),  # Box Drawing (Containers) - Simple range
    "Group E": char_range(0x2190, 50) + char_range(0x2200, 50), # Arrows & Math (Functions)
}

# Category Keywords
KEYWORDS = {
    "Group A": ["tau_", "coefficient", "rate", "constant", "factor", "consumption", "usage", "metabolic", "temperature", "standard_min", "standard_max"],
    "Group B": ["limit", "threshold", "min", "max", "interval", "days", "rules", "schema", "definition", "template", "setting", "mode_prohibited"],
    "Group C": ["current", "is_", "score", "level", "status", "time_since", "accumulated", "probability", "gap", "latency", "count", "balance", "variance", "phase", "weight", "flag"],
    "Group D": ["list", "queue", "buffer", "map", "history", "edges", "dictionary"],
    "Group E": ["calc", "judge", "detect", "estimate", "check", "evaluate", "find", "select", "update", "generate", "convert", "validate", "predict", "assess", "merge"]
}

# Manual Overrides for tricky ones
CATEGORY_OVERRIDE = {
    "constants.txt": "Group A", # Default for constants file if no match
    "variables.txt": "Group C", # Default for variables file
    "transforms.txt": "Group E" # Default for transforms file
}

# --- Parsing Functions ---

def parse_existing_file(filepath: str) -> List[Dict]:
    items = []
    if not os.path.exists(filepath):
        return items
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ":" not in line:
                continue
            
            # Format: Symbol Name: Description
            match = re.match(r"^(\S+)\s+([^:]+):\s*(.+)$", line)
            if match:
                items.append({
                    "name": match.group(2).strip(),
                    "description": match.group(3).strip(),
                    "source": os.path.basename(filepath)
                })
    return items

def parse_proposal_file(filepath: str) -> List[Dict]:
    items = []
    if not os.path.exists(filepath):
        return items
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Pattern 1: **name**: description
    # Pattern 2: **`symbol name` (desc)**
    # Pattern 3: * **name**: desc
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        # Regex for bold items
        # Match: * **name**: description OR * **name** (description)
        match = re.search(r"\*\*\s*[`]?([a-zA-Z0-9_]+)[`]?\s*\*\*", line)
        if match:
            name = match.group(1)
            
            # Try to get description
            description = ""
            # Case: **name**: description
            desc_match = re.search(r"\*\*.+?\*\*[:\s]+(.+)$", line)
            if desc_match:
                description = desc_match.group(1).strip()
            else:
                # Case: **name** (description) - sometimes inside the bold or after
                # Simplified: just take the rest of the line if possible
                pass
            
            # If description is empty, look at next line (simple heuristic)? 
            # For now, let's stick to same line
            
            items.append({
                "name": name,
                "description": description if description else "No description extracted",
                "source": os.path.basename(filepath)
            })
            
    return items

def categorize_item(item: Dict) -> str:
    name = item["name"].lower()
    
    # Check overrides/defaults based on source file
    source = item["source"]
    default_category = CATEGORY_OVERRIDE.get(source, "Group C") # Default to Variable if unknown
    
    # Keyword matching
    for group, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                return group
    
    # Fallback to source-based default
    if source == "constants.txt": return "Group A" # Or B
    if source == "variables.txt": return "Group C" # Or D
    if source == "transforms.txt": return "Group E"
    
    return default_category

# --- Main Process ---

def main():
    all_items = []
    
    # 1. Parse Existing
    print("--- Parsing Existing Files ---")
    for fname in ["constants.txt", "variables.txt", "transforms.txt"]:
        items = parse_existing_file(os.path.join(DATA_DIR, fname))
        print(f"Loaded {len(items)} from {fname}")
        all_items.extend(items)
        
    # 2. Parse Proposals
    print("\n--- Parsing Proposals ---")
    proposal_files = [f for f in os.listdir(PROPOSALS_DIR) if f.endswith(".txt")]
    for fname in proposal_files:
        items = parse_proposal_file(os.path.join(PROPOSALS_DIR, fname))
        print(f"Loaded {len(items)} from {fname}")
        all_items.extend(items)
        
    # Deduplicate by name
    unique_items = {}
    for item in all_items:
        unique_items[item["name"]] = item
    
    print(f"\nTotal Unique Items: {len(unique_items)}")
    
    # 3. Categorize
    categorized = {k: [] for k in SYMBOLS.keys()}
    
    for name, item in unique_items.items():
        category = categorize_item(item)
        categorized[category].append(item)
        
    # 4. Assign Symbols and Output
    print("\n--- Assigning Symbols & Writing ---")
    
    # Mapping Categories to Output Files
    FILE_MAPPING = {
        "Group A": "constants.txt",
        "Group B": "constants.txt",
        "Group C": "variables.txt",
        "Group D": "variables.txt",
        "Group E": "transforms.txt"
    }
    
    output_content = {
        "constants.txt": [],
        "variables.txt": [],
        "transforms.txt": []
    }
    
    for group, items in categorized.items():
        target_file = FILE_MAPPING[group]
        symbols = SYMBOLS[group]
        
        print(f"Processing {group} -> {target_file} ({len(items)} items)")
        
        # Sort items for consistency
        items.sort(key=lambda x: x["name"])
        
        for i, item in enumerate(items):
            if i >= len(symbols):
                print(f"WARNING: Run out of symbols for {group}!")
                symbol = "?"
            else:
                symbol = symbols[i]
            
            line = f"{symbol} {item['name']}: {item['description']}"
            output_content[target_file].append(line)
            
    # Write to files
    for fname, lines in output_content.items():
        path = os.path.join(OUTPUT_DIR, fname)
        with open(path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines) + "\n")
        print(f"Wrote {len(lines)} lines to {fname}")

if __name__ == "__main__":
    main()

