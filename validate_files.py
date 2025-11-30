import json, os, sys

# Load files.json created by yq
# This file contains the JSON array of changes extracted from the model response.
try:
    files = json.load(open('/tmp/files.json'))
except Exception as e:
    # Print error message to stderr (which GitHub Actions captures)
    print(f"❌ Failed to load /tmp/files.json: {e}", file=sys.stderr)
    sys.exit(1)

for f in files:
    # Handle both "FILE" and "file" keys for robust parsing
    path = f.get("FILE") or f.get("file")
    old = f.get("OLD") or ""
    new = f.get("NEW") or ""
    
    if not path:
        sys.exit("❌ Missing FILE path in entry")
    if not os.path.exists(path):
        sys.exit(f"❌ File not found: {path}")
    
    # CONTENT NORMALIZATION AND DEBUGGING 
    # Normalize: replace Windows CRLF with Unix LF, then remove trailing newlines/spaces.
    try:
        current = open(path).read().replace('\r\n', '\n').rstrip()
        old_content = old.replace('\r\n', '\n').rstrip()
    except Exception as e:
        sys.exit(f"❌ Failed to read file {path}: {e}")

    if current != old_content:
        # Add extensive debugging output on failure
        print(f"--- ❌ CONTENT MISMATCH IN {path} ---", file=sys.stderr)
        print(f"Current content length: {len(current)}, OLD content length: {len(old_content)}", file=sys.stderr)
        print("\n--- CURRENT CONTENT ---", file=sys.stderr)
        print(current, file=sys.stderr)
        print("\n--- OLD CONTENT FROM AI ---", file=sys.stderr)
        print(old_content, file=sys.stderr)
        print("\n-------------------------", file=sys.stderr)
        
        sys.exit(f"❌ Content mismatch in {path}")
        
print(f"✅ Parsed and validated {len(files)} files")