"""
📚 INDEX & PAGE SUMMARY GENERATOR (FIXED VERSION)
- Topic Index: Shows topics with page ranges (like book's TOC)
- Page Summary: Shows what's on each page
"""

import json
import re
from pathlib import Path
from collections import defaultdict


class IndexGenerator:
    def __init__(self, raw_text_file):
        """Initialize with the RAW_TEXT file"""
        self.raw_text_file = raw_text_file
        self.page_index_file = raw_text_file.replace("_RAW_TEXT.txt", "_PAGE_INDEX.json")
        
    def extract_complete_toc(self):
        """Extract COMPLETE Table of Contents from PAGE 1 or the entire document"""
        try:
            if not Path(self.raw_text_file).exists():
                return []
                
            with open(self.raw_text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find PAGE 1 content
            page1_match = re.search(r'=== PAGE 1 ===(.*?)=== PAGE 2 ===', content, re.DOTALL)
            if not page1_match:
                # Fallback: extract from entire document
                search_content = content
            else:
                search_content = page1_match.group(1)
            
            # Look for "In this Chapter" section explicitly if it exists
            if "In this Chapter" in search_content:
                # Maybe use the lines following it
                pass
            
            # Extract ALL section headings with multiple patterns
            toc_items = []
            
            # Pattern: matches "2.1 Introduction to Files" or "2.3.1 Opening a file"
            # We look for a number, a dot, a number, then optional dot and number, then text
            pattern = r'(\d+\.\d+(?:\.\d+)?)\s+([A-Z][^\n]{3,80})'
            matches = re.findall(pattern, content) # Search entire document for headings
            
            for section_num, section_title in matches:
                clean_title = ' '.join(section_title.split())
                # Remove common garbage suffixes
                clean_title = clean_title.split('Reprint')[0].strip()
                clean_title = clean_title.split('PAGE')[0].strip()
                
                if len(clean_title) > 3:
                    toc_items.append({
                        'section': section_num,
                        'title': clean_title
                    })
            
            # Deduplicate by section number, keeping first occurrence
            seen = set()
            unique_items = []
            for item in toc_items:
                if item['section'] not in seen:
                    seen.add(item['section'])
                    unique_items.append(item)
            
            return unique_items
            
        except Exception as e:
            print(f"Error extracting TOC: {e}")
            return []
    
    def map_topics_to_pages(self):
        """Map each topic to the pages where it appears"""
        try:
            if not Path(self.raw_text_file).exists():
                return {}
                
            with open(self.raw_text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get all topics from TOC
            toc_items = self.extract_complete_toc()
            if not toc_items:
                return {}
            
            topic_pages = {}
            
            # Find all page markers and their indexes
            page_markers = list(re.finditer(r'=== PAGE (\d+) ===', content))
            
            for item in toc_items:
                section_num = item['section']
                section_title = item['title']
                pages_found = []
                
                for i, marker in enumerate(page_markers):
                    page_num = int(marker.group(1))
                    start_idx = marker.end()
                    end_idx = page_markers[i+1].start() if i+1 < len(page_markers) else len(content)
                    
                    page_content = content[start_idx:end_idx]
                    
                    # Pattern to match the section number as a heading (start of line or after space)
                    if re.search(rf'(?:^|\s){re.escape(section_num)}(?:\s|[A-Z])', page_content):
                        pages_found.append(page_num)
                
                if pages_found:
                    # Consolidate page range
                    if len(pages_found) == 1:
                        page_range = str(pages_found[0])
                    else:
                        # Simple range for now, can be complex like "3-5, 8"
                        # But for a book TOC, it's usually first page or a range
                        if all(pages_found[j] == pages_found[j-1] + 1 for j in range(1, len(pages_found))):
                            page_range = f"{pages_found[0]}-{pages_found[-1]}"
                        else:
                            # Group intervals
                            ranges = []
                            start = pages_found[0]
                            for j in range(1, len(pages_found)):
                                if pages_found[j] != pages_found[j-1] + 1:
                                    if start == pages_found[j-1]:
                                        ranges.append(str(start))
                                    else:
                                        ranges.append(f"{start}-{pages_found[j-1]}")
                                    start = pages_found[j]
                            if start == pages_found[-1]:
                                ranges.append(str(start))
                            else:
                                ranges.append(f"{start}-{pages_found[-1]}")
                            page_range = ", ".join(ranges)
                    
                    topic_pages[section_num] = {
                        'title': section_title,
                        'pages': page_range
                    }
            
            return topic_pages
            
        except Exception as e:
            print(f"Error mapping topics: {e}")
            return {}
            
    def generate_topic_index_table(self):
        """Generate TOPIC-WISE index (like book's TOC)"""
        topic_map = self.map_topics_to_pages()
        
        if not topic_map:
            return "Could not generate topic index"
        
        table = "| Section | Topic | Pages |\n"
        table += "|---------|-------|-------|\n"
        
        def sort_key(s):
            try:
                return [int(n) for n in s.split('.')]
            except:
                return [0]
                
        for section_num in sorted(topic_map.keys(), key=sort_key):
            item = topic_map[section_num]
            table += f"| {section_num} | {item['title']} | {item['pages']} |\n"
        
        return table
        
    def generate_page_summary_table(self):
        """Generate PAGE-WISE summary - FIXED VERSION"""
        try:
            if not Path(self.raw_text_file).exists():
                return "Raw text file missing"
                
            with open(self.raw_text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            summaries = []
            
            page_num = 1
            while True:
                page_marker_start = f"=== PAGE {page_num} ==="
                next_page = page_num + 1
                page_marker_end = f"=== PAGE {next_page} ==="
                
                start_idx = content.find(page_marker_start)
                if start_idx == -1:
                    if page_num > 1: break # End of document
                    page_num += 1
                    continue
                
                end_idx = content.find(page_marker_end)
                
                if end_idx == -1:
                    page_content = content[start_idx:]
                else:
                    page_content = content[start_idx:end_idx]
                
                # CRITICAL FIX: Remove ONLY big separator bars, keep everything else
                clean_content = re.sub(r'^={15,}.*$', '', page_content, flags=re.MULTILINE).strip()
                clean_content = re.sub(r'\n\s*\n', '\n', clean_content).strip()
                
                if clean_content and len(clean_content) > 10:
                    # Has real content - extract first meaningful line
                    lines = [l.strip() for l in clean_content.split('\n') 
                            if l.strip() and len(l.strip()) > 5]
                    
                    if lines:
                        summary = lines[0][:100]
                    else:
                        summary = "(Content available - no clear heading)"
                else:
                    # Empty page - mark clearly
                    summary = "============================================================"
                
                summaries.append({
                    'page': page_num,
                    'summary': summary
                })
                
                page_num += 1
                if page_num > 100: break # Safety break
            
            # Create table
            table = "| Page | Content Summary |\n"
            table += "|------|------------------|\n"
            
            for item in summaries:
                summary_text = item['summary']
                # Only clean if it's NOT the empty page marker
                if "======" not in summary_text:
                    clean_summary = summary_text.replace('=', '').strip()
                    if not clean_summary:
                        clean_summary = "Continued content"
                else:
                    clean_summary = summary_text
                
                table += f"| {item['page']} | {clean_summary} |\n"
            
            return table
            
        except Exception as e:
            print(f"Error generating page summary: {e}")
            return "Could not generate page summaries"

def generate_topic_index(pdf_name):
    base_name = Path(pdf_name).stem
    raw_text_file = f"documents/{base_name}_RAW_TEXT.txt"
    if not Path(raw_text_file).exists(): return "File not found"
    return IndexGenerator(raw_text_file).generate_topic_index_table()

def generate_page_summary(pdf_name):
    base_name = Path(pdf_name).stem
    raw_text_file = f"documents/{base_name}_RAW_TEXT.txt"
    if not Path(raw_text_file).exists(): return "File not found"
    return IndexGenerator(raw_text_file).generate_page_summary_table()
