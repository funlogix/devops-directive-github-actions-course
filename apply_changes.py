import json, os, sys, shutil

# The FILES_JSON is passed as an environment variable to the shell,
# which needs to be passed to the Python script somehow.
# Since we can't easily access shell environment variables passed with '''${{ env.FILES_JSON }}''' 
# directly in the standalone script without command-line arguments, 
# we'll rely on the calling step to pass the content.

# We'll expect the calling step to write the JSON content to a temporary file,
# or we can read it from an argument.

# For simplicity, let's assume the calling shell step writes the JSON to a file named /tmp/files.json 
# OR we rely on the SHELL to pass the environment variable content directly (which is what the old step did).

# To replicate the old behavior: read the variable content from the first command-line argument (sys.argv[1])
# NOTE: The calling shell step *must* be modified to pass ${{ env.FILES_JSON }} as an argument.

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
    # Ensure keys are lowercase as they are pulled from the JSON output
    path = f.get('file')
    new_content = f.get('new')

    if not path or new_content is None:
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