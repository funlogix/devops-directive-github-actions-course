import json
import os
import sys
import shutil

# --- Data Loading ---
# The script relies on the preceding workflow step writing the
# FILES_JSON content to /tmp/files.json.

try:
    with open('/tmp/files.json', 'r') as f_json:
        files = json.load(f_json)
except FileNotFoundError:
    # This should only happen if the preceding workflow step failed to run or write the file.
    sys.exit("❌ Error: /tmp/files.json not found. Check the 'Parse Model Response' step.")
except Exception as e:
    sys.exit(f"❌ Failed to parse /tmp/files.json: {e}")

if not isinstance(files, list):
    sys.exit("❌ FILES content is not a list")

# --- Apply Changes ---
for f in files:
    # Use case-insensitive retrieval for robustness against varying LLM/yq output.
    # Checks for 'file' (lowercase) OR 'FILE' (uppercase).
    path = f.get('file') or f.get('FILE') 
    
    # Checks for 'new' (lowercase) OR 'NEW' (uppercase).
    new_content = f.get('new') or f.get('NEW')

    if not path or new_content is None:
        # Exit if file path or new content is missing (most likely due to truncation or malformed JSON)
        sys.exit(f"❌ Missing required fields (FILE/NEW) in entry: {f}")

    if not os.path.exists(path):
        # Exit if the target file doesn't exist (LLM error)
        sys.exit(f"❌ Target file does not exist: {path}")

    # 1. Backup original file for safety
    backup_path = path + ".bak"
    try:
        shutil.copy(path, backup_path)
        print(f"📦 Backed up {path} to {backup_path}")
    except Exception as e:
        sys.exit(f"❌ Failed to create backup of {path}: {e}")


    # 2. Write new content with UTF-8 encoding
    try:
        # We use 'w' mode, which truncates/overwrites the file.
        with open(path, 'w', encoding='utf-8') as fp:
            fp.write(new_content)
        print(f"✅ Updated {path}")
    except Exception as e:
        # If writing fails, exit immediately
        sys.exit(f"❌ Failed to update {path}: {e}")

# Script exits successfully (exit code 0) if all changes are applied.