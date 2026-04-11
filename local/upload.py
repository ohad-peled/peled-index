import os
import sys

if len(sys.argv) < 2:
    print("Usage: python upload.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]
dest = "/app/data/phd_isr_res_filtered.json"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

with open(file_path, 'rb') as src:
    with open(dest, 'wb') as dst:
        dst.write(src.read())

print(f"✓ Uploaded to {dest}")