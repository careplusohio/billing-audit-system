import subprocess

# Step 1: Import
try:
    print("Starting import...")
    subprocess.run(["python", "import_rhino_claims.py"], check=True)
    print("✅ Import completed.")
except subprocess.CalledProcessError as e:
    print(f"❌ Import failed: {e}")

# Step 2: Export
try:
    print("Starting export...")
    subprocess.run(["python", "export_rhino_claims.py"], check=True)
    print("✅ Export completed.")
except subprocess.CalledProcessError as e:
    print(f"❌ Export failed: {e}")
