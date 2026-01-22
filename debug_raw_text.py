"""Debug script to analyze RAW_TEXT file structure"""

from pathlib import Path
import re

raw_file = "documents/computer 12ch2_RAW_TEXT.txt"

if not Path(raw_file).exists():
    print("❌ File not found!")
    exit(1)

with open(raw_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 60)
print("ANALYZING RAW_TEXT FILE")
print("=" * 60)

# Count pages
page_markers = re.findall(r'=== PAGE (\d+) ===', content)
print(f"\n📄 Total pages found: {len(page_markers)}")
print(f"   Pages: {', '.join(page_markers[:10])}...")

# Analyze PAGE 1
print("\n" + "=" * 60)
print("PAGE 1 CONTENT (First 1000 chars)")
print("=" * 60)

page1_match = re.search(r'=== PAGE 1 ===(.*?)=== PAGE 2 ===', content, re.DOTALL)
if page1_match:
    page1_content = page1_match.group(1)
    print(page1_content[:1000])
    
    # Find sections on page 1
    # Improved pattern for detecting sections like "2.1 Introduction to Files"
    sections = re.findall(r'(\d+\.\d+(?:\.\d+)?)\s+([A-Z][^\n]{3,80})', content)
    print("\n📋 All Sections found in document (first 20):")
    seen = set()
    count = 0
    for sec_num, sec_title in sections:
        if sec_num not in seen:
            print(f"  {sec_num} - {sec_title[:50].strip()}")
            seen.add(sec_num)
            count += 1
            if count >= 20: break
else:
    print("❌ Could not extract PAGE 1")

# Analyze PAGE 4
print("\n" + "=" * 60)
print("PAGE 4 CONTENT (First 500 chars)")
print("=" * 60)

page4_match = re.search(r'=== PAGE 4 ===(.*?)=== PAGE 5 ===', content, re.DOTALL)
if page4_match:
    page4_content = page4_match.group(1)
    print(page4_content[:500])
    
    if "Table 2.1" in page4_content:
        print("\n✅ Found 'Table 2.1' on Page 4!")
    else:
        print("\n❌ 'Table 2.1' NOT found on Page 4.")
else:
    print("❌ Could not extract PAGE 4")
