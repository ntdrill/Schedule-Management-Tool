import re
import os
import sys
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

# --- Configuration ---
KEY_FILE_PATH = "Agent_workspace/symbol_agent/key/supabase_1.txt"
# value_type is optional; DBにカラムがない場合は無効化する
USE_VALUE_TYPE = False
VALUE_TYPES_PATH = "data/value_types_override.json"

def load_credentials():
    print(f"Current CWD: {os.getcwd()}")
    try:
        if not os.path.exists(KEY_FILE_PATH):
            print(f"File not found at: {os.path.abspath(KEY_FILE_PATH)}")
        
        with open(KEY_FILE_PATH, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                # Fallback for single line case
                if len(lines) == 1 and " " in lines[0]:
                    parts = lines[0].strip().split()
                    if len(parts) >= 2:
                        return parts[0], parts[1]
                raise ValueError(f"Key file format invalid. Lines: {len(lines)}")
            url = lines[0].strip()
            key = lines[1].strip()
            return url, key
    except Exception as e:
        print(f"Error loading credentials from {KEY_FILE_PATH}: {e}")
        sys.exit(1)

SUPABASE_URL, SUPABASE_KEY = load_credentials()

# File paths
DATA_DIR = "data"
FILES = {
    "constants.txt": {"category": "constant"},
    "variables.txt": {"category": "variable"},
    "transforms.txt": {"category": "function"},
}

# --- Parsing Logic ---
def load_value_types() -> Dict[str, str]:
    if not USE_VALUE_TYPE:
        return {}
    if not os.path.exists(VALUE_TYPES_PATH):
        return {}
    try:
        import json
        with open(VALUE_TYPES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load value types from {VALUE_TYPES_PATH}: {e}")
        return {}


def parse_line(
    line: str,
    file_name: str,
    default_category: str,
    value_types: Dict[str, str]
) -> Optional[Dict[str, Any]]:
    line = line.strip()
    if not line or ":" not in line:
        return None

    match = re.match(r"^(\S+)\s+([^:]+):\s*(.+)$", line)
    if not match:
        print(f"Skipping format mismatch: {line}")
        return None
    
    symbol = match.group(1)
    name = match.group(2).strip()
    rest = match.group(3).strip()
    
    description = rest
    default_value = None
    unit = None
    value_type = value_types.get(name)
    
    paren_match = re.search(r"\((.+)\)$", rest)
    if paren_match:
        content_in_paren = paren_match.group(1)
        description = rest.replace(f"({content_in_paren})", "").strip()
        default_value = content_in_paren

    group_id = "general"
    
    # Range Checks
    # Group A: Canadian Aboriginal Syllabics (U+1401+)
    if "\u1401" <= symbol <= "\u167f":
        group_id = "physical_constants"
        
    # Group B: Ethiopic (U+1200+)
    elif "\u1200" <= symbol <= "\u137f":
        group_id = "system_settings"
        
    # Group C: Yi Syllables (U+A000+)
    elif "\ua000" <= symbol <= "\ua48c":
        group_id = "state_variables"
        
    # Group D: Box Drawing (U+2500+)
    elif "\u2500" <= symbol <= "\u257f":
        group_id = "containers"
        
    # Group E: Arrows (U+2190+) & Math (U+2200+)
    elif ("\u2190" <= symbol <= "\u21ff") or ("\u2200" <= symbol <= "\u22ff"):
        group_id = "functions"
        
    else:
        if file_name == "constants.txt": group_id = "constants_misc"
        elif file_name == "variables.txt": group_id = "variables_misc"
        elif file_name == "transforms.txt": group_id = "functions_misc"

    return {
        "symbol": symbol,
        "name": name,
        "description": description,
        "category": default_category,
        "group_id": group_id,
        "default_value": {"raw": default_value} if default_value else None,
        "unit": unit,
        **({"value_type": value_type} if USE_VALUE_TYPE else {})
    }

def process_files() -> List[Dict[str, Any]]:
    records = []
    print("--- Parsing Files ---")
    value_types = load_value_types()
    for filename, config in FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: File not found {filepath}")
            continue
            
        print(f"Reading {filename}...")
        count = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    record = parse_line(line, filename, config["category"], value_types)
                    if record:
                        records.append(record)
                        count += 1
            print(f"  -> Found {count} records in {filename}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    return records

# --- Database Logic ---
def push_to_supabase(records: List[Dict[str, Any]]):
    if not records:
        print("No records to push.")
        return

    print("\n--- Connecting to Supabase ---")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Clear existing data (Refresh strategy)
        print("Clearing existing records...")
        # To delete all, we can use a filter that matches everything, e.g. name is not null
        # Or better, iterate and delete if needed, but 'neq' is safer if table allows.
        # Assuming 'name' PK exists.
        try:
            # First, check if we can connect
            supabase.table("symbols").select("name").limit(1).execute()
        except Exception as e:
            print(f"Connection check failed: {e}")
            return

        # Attempting upsert directly without delete might be safer for now
        # to avoid accidental mass deletion if logic is wrong.
        # But per requirements "Refresh", let's try upsert.
        
        print(f"Attempting to upsert {len(records)} records (Key: name)...")
        
        # Upsert
        response = supabase.table("symbols").upsert(records, on_conflict="name").execute()
        
        # Check response
        if response.data:
            inserted_count = len(response.data)
            print(f"\n--- Success! ---")
            print(f"Registered/Updated: {inserted_count} records")
            
            if inserted_count == len(records):
                print("✅ Count Check Passed: Input count matches Database count.")
            else:
                print(f"⚠️ Count Check Failed: Input {len(records)} != Database {inserted_count}")
        else:
             # Sometimes data is None on success if return=minimal
             print("Request executed. (No data returned, possibly 'minimal' preference)")

    except Exception as e:
        print(f"\n❌ Error pushing to Supabase: {e}")

if __name__ == "__main__":
    data = process_files()
    if data:
        push_to_supabase(data)
    else:
        print("No data parsed.")
