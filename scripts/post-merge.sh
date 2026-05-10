#!/bin/bash
set -e
pnpm install --frozen-lockfile
pnpm --filter db push

# Fix garbage bytes that sometimes appear at the start of driving_school_single.py
# after a merge (task agents occasionally prepend stray Arabic chars before the
# coding declaration, causing NameError on Windows at startup).
python3 - <<'EOF'
import sys, os
path = "driving_school_single.py"
if not os.path.exists(path):
    sys.exit(0)
with open(path, "rb") as f:
    data = f.read()
if data.startswith(b"# -*-"):
    sys.exit(0)
idx = data.find(b"# -*- coding")
if idx <= 0:
    sys.exit(0)
print(f"post-merge: stripping {idx} garbage byte(s) from start of {path}: {data[:idx]!r}")
with open(path, "wb") as f:
    f.write(data[idx:])
EOF
