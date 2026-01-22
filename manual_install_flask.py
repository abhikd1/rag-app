"""
Manual Flask Installation Script
Since pip is not working, this extracts and installs Flask manually
"""

import sys
import zipfile
import shutil
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*60)
print("MANUAL FLASK INSTALLATION")
print("="*60)

# Flask wheel file
wheel_file = "flask-3.1.2-py3-none-any.whl"

if not Path(wheel_file).exists():
    print(f"❌ {wheel_file} not found!")
    print("Please download Flask wheel file first.")
    sys.exit(1)

print(f"✅ Found: {wheel_file}")

# Extract wheel (it's just a zip file)
print("\n📦 Extracting Flask...")
try:
    with zipfile.ZipFile(wheel_file, 'r') as zip_ref:
        zip_ref.extractall("flask_temp")
    print("✅ Extracted successfully")
except Exception as e:
    print(f"❌ Extraction failed: {e}")
    sys.exit(1)

# Get Python site-packages directory
import site
site_packages = site.getsitepackages()[0]
print(f"\n📂 Python site-packages: {site_packages}")

# Copy Flask to site-packages
print("\n📋 Installing Flask...")
try:
    flask_src = Path("flask_temp/flask")
    flask_dst = Path(site_packages) / "flask"
    
    if flask_dst.exists():
        print("⚠️ Flask already exists, removing old version...")
        shutil.rmtree(flask_dst)
    
    shutil.copytree(flask_src, flask_dst)
    print("✅ Flask installed!")
    
    # Copy metadata
    metadata_src = Path("flask_temp/flask-3.1.2.dist-info")
    metadata_dst = Path(site_packages) / "flask-3.1.2.dist-info"
    
    if metadata_dst.exists():
        shutil.rmtree(metadata_dst)
    
    shutil.copytree(metadata_src, metadata_dst)
    print("✅ Metadata installed!")
    
except Exception as e:
    print(f"❌ Installation failed: {e}")
    sys.exit(1)

# Cleanup
print("\n🧹 Cleaning up...")
shutil.rmtree("flask_temp")

print("\n" + "="*60)
print("✅ FLASK INSTALLED SUCCESSFULLY!")
print("="*60)

# Verify
print("\n🔍 Verifying installation...")
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
    print("\n🎉 Flask is ready to use!")
except ImportError:
    print("❌ Flask import failed. Please restart Python.")

print("\n📝 Next steps:")
print("1. Download flask-cors wheel file")
print("2. Run this script again for flask-cors")
print("3. Run: python ultimate_server.py")
