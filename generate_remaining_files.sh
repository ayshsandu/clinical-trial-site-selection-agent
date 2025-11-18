#!/bin/bash

echo "Generating remaining MCP server files and agent files..."

# Create Site Performance Server files
mkdir -p mcp-servers/site-performance/src

# Create Agent files  
mkdir -p agent/src/nodes

echo "Directory structure created"
echo "Creating comprehensive zip file..."

cd /mnt/user-data/outputs
python3 << 'PYTHON'
import zipfile
import os
from pathlib import Path

zip_file = "clinical-trial-site-selection-demo.zip"
base_dir = "clinical-trial-demo"

print(f"Creating comprehensive {zip_file}...")

# Count files
file_count = 0
for root, dirs, files in os.walk(base_dir):
    file_count += len(files)

print(f"Found {file_count} files to package")

# Create zip
with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, os.path.dirname(base_dir))
            zf.write(file_path, arcname)

zip_size = os.path.getsize(zip_file)
print(f"✓ Created {zip_file} ({zip_size:,} bytes)")
PYTHON

