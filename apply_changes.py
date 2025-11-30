import json, os, sys, shutil

# The FILES_JSON is passed as an environment variable to the shell,
# which needs to be passed to the Python script somehow.
# Since we can't easily access shell environment variables passed with '''${{ env.FILES_JSON }}''' 
# directly in the standalone script without command-line arguments, 
# we'll rely on the calling step to pass the content.

# We'll expect the calling step to write the JSON content to a temporary file,
# or we can rely on the SHELL to pass the environment variable content directly (which is what the old step did).

if len(sys.argv) < 2:
    sys.exit("❌ Missing FILES_JSON argument")

files_json_string = sys.argv[1]

try:
    # Use json.loads to parse the string passed from the shell
    files = json.loads(files_json_string)
except Exception as e:
    sys.exit(f"❌ Failed to parse FILES_JSON: {e}")

if not isinstance(files, list):
    sys.exit("❌ FILES_JSON is not a list")

for f in files:
    # --- CHANGE START ---
    # Try getting the field using lowercase, but fall back to uppercase if needed.
    # The 'or' operator works because f.get() returns None if the key doesn't exist.
    path = f.get('file') or f.get('FILE') 
    new_content = f.get('new') or f.get('NEW')
    # --- CHANGE END ---

    if not path or new_content is None:
        # This will catch cases where either 'file'/'FILE' or 'new'/'NEW' is missing/None
        sys.exit(f"❌ Missing required fields in entry: {f}")

    if not os.path.exists(path):
        sys.exit(f"❌ Target file does not exist: {path}")

    # Backup original file for safety
    backup_path = path + ".bak"
    shutil.copy(path, backup_path)
    print(f"📦 Backed up {path} to {backup_path}")

    # Write new content with UTF-8 encoding
    try:
        with open(path, 'w', encoding='utf-8') as fp:
            fp.write(new_content)
        print(f"✅ Updated {path}")
    except Exception as e:
        sys.exit(f"❌ Failed to update {path}: {e}")