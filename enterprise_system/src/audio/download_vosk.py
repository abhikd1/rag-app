"""Download Vosk model"""
import urllib.request
import zipfile
import os

model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
zip_path = "vosk-model.zip"
extract_dir = "."

print("Downloading Vosk model (40MB)...")
urllib.request.urlretrieve(model_url, zip_path)

print("Extracting...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

os.remove(zip_path)
print("✓ Vosk model ready!")
