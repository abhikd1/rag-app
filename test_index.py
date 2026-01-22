"""Test script to verify index generation"""

from index_generator import IndexGenerator
from pathlib import Path

# Test with your PDF
raw_text_file = "documents/computer 12ch2_RAW_TEXT.txt"

if not Path(raw_text_file).exists():
    print("❌ RAW_TEXT file not found!")
    exit(1)

generator = IndexGenerator(raw_text_file)

print("=" * 60)
print("TEST 1: Extracting TOC")
print("=" * 60)
toc = generator.extract_complete_toc()
print(f"Found {len(toc)} topics:")
for item in toc[:20]:
    print(f"  {item['section']} - {item['title']}")

print("\n" + "=" * 60)
print("TEST 2: Mapping topics to pages")
print("=" * 60)
topic_map = generator.map_topics_to_pages()
print(f"Mapped {len(topic_map)} topics:")

def sort_key(s):
    try: return [int(n) for n in s.split('.')]
    except: return [0]

for section in sorted(topic_map.keys(), key=sort_key):
    data = topic_map[section]
    print(f"  {section} | {data['title'][:40]} | Pages {data['pages']}")

print("\n" + "=" * 60)
print("TEST 3: Generate Topic Index Table")
print("=" * 60)
print(generator.generate_topic_index_table())
