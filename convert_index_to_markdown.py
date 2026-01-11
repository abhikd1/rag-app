
import os
import re

def convert_index_to_md(input_file, output_file):
    print(f"Reading {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    md_content = ["# 📘 COMPLETE DBMS BOOK INDEX\n"]
    md_content.append(f"**Source:** {os.path.basename(input_file)}")
    md_content.append(f"**Total Entries:** {len(lines)}\n")
    
    md_content.append("| # | SECTION / TOPIC | PAGE |")
    md_content.append("|---|---|---|")
    
    count = 1
    for line in lines:
        line = line.strip()
        if not line or line.startswith("==="): continue
        
        # Clean up line
        topic = ""
        page = ""
        
        if "→" in line:
            # Sub topics with page numbers: -> Topic (Page X)
            try:
                parts = line.split("(Page")
                topic = parts[0].replace("→", "").strip()
                page = parts[1].replace(")", "").strip() if len(parts) > 1 else ""
            except:
                topic = line.replace("→", "").strip()
        elif line.startswith("📖"):
            topic = f"**{line.replace('📖', '').strip()}**"
            page = "-"
        else:
            topic = line
            
        # Escape pipe characters for markdown table
        topic = topic.replace("|", "-")
        
        md_content.append(f"| {count} | {topic} | {page} |")
        count += 1

    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    print("✅ Done!")

if __name__ == "__main__":
    input_path = r"c:\Users\sumit\rag app\documents\dbms_INDEX.txt"
    output_path = r"c:\Users\sumit\rag app\DBMS_FULL_INDEX.md"
    convert_index_to_md(input_path, output_path)
