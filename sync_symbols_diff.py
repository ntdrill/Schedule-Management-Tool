import re
import os
import sys
import json
from typing import List, Dict, Any, Optional
from supabase import create_client, Client

# --- Configuration ---
KEY_FILE_PATH = "Agent_workspace/symbol_agent/key/supabase_1.txt"

def load_credentials():
    print(f"Current CWD: {os.getcwd()}")
    try:
        if not os.path.exists(KEY_FILE_PATH):
            print(f"File not found at: {os.path.abspath(KEY_FILE_PATH)}")
        
        with open(KEY_FILE_PATH, 'r') as f:
            lines = f.readlines()
            # print(f"Debug: Lines read from key file: {lines}") # Debug output suppressed
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
def parse_line(line: str, file_name: str, default_category: str) -> Optional[Dict[str, Any]]:
    line = line.strip()
    if not line or ":" not in line:
        return None

    match = re.match(r"^(\S+)\s+([^:]+):\s*(.+)$", line)
    if not match:
        # print(f"Skipping format mismatch: {line}")
        return None
    
    symbol = match.group(1)
    name = match.group(2).strip()
    rest = match.group(3).strip()
    
    description = rest
    default_value = None
    unit = None
    
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
        "unit": unit
    }

def process_files() -> List[Dict[str, Any]]:
    records = []
    print("--- Parsing Files ---")
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
                    record = parse_line(line, filename, config["category"])
                    if record:
                        records.append(record)
                        count += 1
            print(f"  -> Found {count} records in {filename}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    return records

# --- Database Logic ---

def fetch_existing_symbols(supabase: Client) -> Dict[str, Dict[str, Any]]:
    print("\nFetching existing symbols from DB...")
    try:
        # Fetch all records. Assuming the total count is < 10000. 
        # If larger, pagination is needed.
        response = supabase.table("symbols").select("*").limit(10000).execute()
        if response.data:
            existing_map = {row["name"]: row for row in response.data}
            print(f"  -> Fetched {len(existing_map)} records.")
            return existing_map
        return {}
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        sys.exit(1)

def is_different(local_record: Dict[str, Any], db_record: Dict[str, Any]) -> bool:
    # Compare fields that are managed by the text files
    # Keys to compare: symbol, description, category, group_id, default_value, unit
    
    keys_to_compare = ["symbol", "description", "category", "group_id", "unit"]
    
    for key in keys_to_compare:
        local_val = local_record.get(key)
        db_val = db_record.get(key)
        
        # Normalize None vs "" if necessary, but here we expect None in local implies NULL in DB
        if local_val != db_val:
            # print(f"Diff in {local_record['name']}.{key}: Local='{local_val}' vs DB='{db_val}'")
            return True

    # Special handling for JSONB default_value
    local_dv = local_record.get("default_value")
    db_dv = db_record.get("default_value")
    
    # Simple comparison for dictionaries/None
    if local_dv != db_dv:
        # print(f"Diff in {local_record['name']}.default_value: Local='{local_dv}' vs DB='{db_dv}'")
        return True
        
    return False

def push_diff_to_supabase(local_records: List[Dict[str, Any]]):
    if not local_records:
        print("No local records found.")
        return

    print("\n--- Connecting to Supabase ---")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Fetch existing data
        db_map = fetch_existing_symbols(supabase)
        
        # 2. Calculate Diff
        to_upsert = []
        new_count = 0
        update_count = 0
        
        for record in local_records:
            name = record["name"]
            if name not in db_map:
                # New record
                to_upsert.append(record)
                new_count += 1
            else:
                # Existing record, check for changes
                if is_different(record, db_map[name]):
                    to_upsert.append(record)
                    update_count += 1
        
        print(f"\n--- Diff Calculation ---")
        print(f"Total Local Records: {len(local_records)}")
        print(f"New Records: {new_count}")
        print(f"Updated Records: {update_count}")
        print(f"Unchanged Records: {len(local_records) - len(to_upsert)}")
        
        if not to_upsert:
            print("\n✅ No changes detected. Database is up to date.")
            return

        print(f"\nAttempting to upsert {len(to_upsert)} records (New + Updated)...")
        
        # Upsert
        response = supabase.table("symbols").upsert(to_upsert, on_conflict="name").execute()
        
        # Check response
        if response.data:
            inserted_count = len(response.data)
            print(f"\n--- Success! ---")
            print(f"Processed: {inserted_count} records")
        else:
             print("Request executed. (No data returned)")

    except Exception as e:
        print(f"\n❌ Error pushing to Supabase: {e}")

if __name__ == "__main__":
    data = process_files()
    if data:
        push_diff_to_supabase(data)
    else:
        print("No data parsed.")

