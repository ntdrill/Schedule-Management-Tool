import re
import os
import sys
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
            print(f"Debug: Lines read from key file: {lines}")
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
    "coping_actions.txt": {"table": "coping_actions", "type": "action"},
    "coping_scenarios.txt": {"table": "coping_scenarios", "type": "scenario"},
}

# --- Parsing Logic ---
def parse_action_line(line: str) -> Optional[Dict[str, Any]]:
    """対処行動の行をパース: name|category|effectiveness|ease_of_use|recommendation|description"""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    
    parts = line.split("|")
    if len(parts) < 6:
        print(f"Skipping format mismatch: {line}")
        return None
    
    return {
        "name": parts[0].strip(),
        "category": parts[1].strip(),
        "effectiveness_rating": int(parts[2].strip()) if parts[2].strip().isdigit() else None,
        "ease_of_use_rating": int(parts[3].strip()) if parts[3].strip().isdigit() else None,
        "recommendation_rating": int(parts[4].strip()) if parts[4].strip().isdigit() else None,
        "description": parts[5].strip() if len(parts) > 5 else "",
    }

def parse_scenario_line(line: str) -> Optional[Dict[str, Any]]:
    """場面の行をパース: name|category|severity_level|description"""
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    
    parts = line.split("|")
    if len(parts) < 4:
        print(f"Skipping format mismatch: {line}")
        return None
    
    return {
        "name": parts[0].strip(),
        "category": parts[1].strip(),
        "severity_level": parts[2].strip(),
        "description": parts[3].strip() if len(parts) > 3 else "",
    }

def process_files() -> Dict[str, List[Dict[str, Any]]]:
    """ファイルを読み込んでパース"""
    records = {}
    print("--- Parsing Files ---")
    
    for filename, config in FILES.items():
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: File not found {filepath}")
            continue
        
        print(f"Reading {filename}...")
        count = 0
        file_records = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if config["type"] == "action":
                        record = parse_action_line(line)
                    else:
                        record = parse_scenario_line(line)
                    
                    if record:
                        file_records.append(record)
                        count += 1
            
            print(f"  -> Found {count} records in {filename}")
            records[config["table"]] = file_records
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    return records

# --- Database Logic ---
def push_to_supabase(records: Dict[str, List[Dict[str, Any]]]):
    """Supabaseにデータを登録"""
    if not records:
        print("No records to push.")
        return

    print("\n--- Connecting to Supabase ---")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        for table_name, table_records in records.items():
            if not table_records:
                print(f"\nSkipping {table_name}: No records")
                continue
            
            print(f"\n--- Processing {table_name} ---")
            print(f"Attempting to upsert {len(table_records)} records...")
            
            # 接続確認
            try:
                supabase.table(table_name).select("name").limit(1).execute()
            except Exception as e:
                print(f"Connection check failed for {table_name}: {e}")
                print("Please ensure the table exists in Supabase.")
                continue
            
            # Upsert (nameをキーとして)
            try:
                response = supabase.table(table_name).upsert(
                    table_records, 
                    on_conflict="name"
                ).execute()
                
                if response.data:
                    inserted_count = len(response.data)
                    print(f"✅ Success! Registered/Updated: {inserted_count} records in {table_name}")
                    
                    if inserted_count == len(table_records):
                        print(f"✅ Count Check Passed: Input {len(table_records)} == Database {inserted_count}")
                    else:
                        print(f"⚠️ Count Check Warning: Input {len(table_records)} != Database {inserted_count}")
                else:
                    print(f"Request executed for {table_name}. (No data returned, possibly 'minimal' preference)")
                    
            except Exception as e:
                print(f"❌ Error upserting to {table_name}: {e}")
                print(f"   First record example: {table_records[0] if table_records else 'N/A'}")
        
        print("\n--- Summary ---")
        total = sum(len(recs) for recs in records.values())
        print(f"Total records processed: {total}")

    except Exception as e:
        print(f"\n❌ Error connecting to Supabase: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Coping Data Migration Script")
    print("=" * 60)
    
    data = process_files()
    if data:
        push_to_supabase(data)
    else:
        print("No data parsed.")


