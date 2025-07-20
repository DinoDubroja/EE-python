def separator(title):
    print(f"\n=== {title} ===")

# === File I/O and Context Managers Syntax ===
# Demonstration of File I/O and Context Managers in Python

def separator(title):
    print(f"\n=== {title} ===")

# 1. Writing text to a file
separator("1. Writing text to a file")
with open("example.txt", "w") as f:
    f.write("Line 1\n")
    f.write("Line 2\n")
print("Wrote example.txt")

# 2. Reading entire file content
separator("2. Reading entire file content")
with open("example.txt", "r") as f:
    content = f.read()
print(content)

# 3. Reading line by line
separator("3. Reading file line by line")
with open("example.txt", "r") as f:
    for line in f:
        print(f"Line read: {line.strip()}")

# 4. Appending to a file
separator("4. Appending to a file")
with open("example.txt", "a") as f:
    f.write("Line 3 appended\n")
# Verify append
with open("example.txt", "r") as f:
    print(f.read())

# 5. Binary file write/read
separator("5. Binary file write/read")
data = bytes(range(10))  # 0x00,0x01,...0x09
with open("example.bin", "wb") as bf:
    bf.write(data)
with open("example.bin", "rb") as bf:
    bin_content = bf.read()
print("Binary content:", bin_content)

# 6. Handling missing file with exception
separator("6. Handling missing file")
try:
    with open("nonexistent.txt", "r") as f:
        pass
except FileNotFoundError as e:
    print("Caught FileNotFoundError:", e)

# 7. Using pathlib for file paths
separator("7. Using pathlib")
from pathlib import Path
p = Path("example.txt")
print(f"Exists? {p.exists()}, Size? {p.stat().st_size} bytes")

# 8. Writing CSV using csv module
separator("8. CSV write/read")
import csv
rows = [["time_s", "voltage"], [0.0, 1.2], [0.1, 1.4]]
with open("data.csv", "w", newline="") as csvf:
    writer = csv.writer(csvf)
    writer.writerows(rows)
with open("data.csv", "r", newline="") as csvf:
    reader = csv.reader(csvf)
    for r in reader:
        print(r)

# 9. JSON serialization/deserialization
separator("9. JSON write/read")
import json
obj = {"sensor": "temp", "values": [22.5, 23.0, 22.8]}
with open("data.json", "w") as jf:
    json.dump(obj, jf)
with open("data.json", "r") as jf:
    loaded = json.load(jf)
print("Loaded JSON:", loaded)

# 10. Custom context manager using 'contextlib'
separator("10. Custom context manager")
from contextlib import contextmanager

@contextmanager
def open_and_log(filename, mode):
    print(f"Opening {filename} in mode '{mode}'")
    f = open(filename, mode)
    try:
        yield f
    finally:
        f.close()
        print(f"Closed {filename}")

with open_and_log("log.txt", "w") as logf:
    logf.write("Log entry\n")
