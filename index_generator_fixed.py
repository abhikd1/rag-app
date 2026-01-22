"""
📚 FIXED INDEX GENERATOR
Shows hierarchical topic structure matching the book's index
"""

import json
import re
from pathlib import Path
from collections import defaultdict


class HierarchicalIndexGenerator:
    def __init__(self, raw_text_file):
        """Initialize with the RAW_TEXT file"""
        self.raw_text_file = raw_text_file
        
    def extract_all_topics(self):
        """Extract ALL topics from the entire document"""
        try:
            with open(self.raw_text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract ALL section headings from ENTIRE document
            # Improved Pattern: Must be at the start of a line to be a real heading
            # Matches "2.X", "2.X.X", "2.X.X.X" at start of line
            pattern = r'(?m)^(\d+\.\d+(?:\.\d+)?(?:\.\d+)?)\.?\s+([A-Z][^\n]{3,100})'
            matches = re.findall(pattern, content)
            
            all_topics = {}
            
            for section_num, section_title in matches:
                # Clean up title
                clean_title = ' '.join(section_title.split())
                clean_title = clean_title.replace('Reprint 2025-26', '').strip()
                
                # Skip if title is too short or invalid
                if len(clean_title) < 3 or clean_title.startswith('PAGE'):
                    continue
                
                # Add to dictionary (key: section number)
                if section_num not in all_topics:
                    all_topics[section_num] = clean_title
            
            return all_topics
            
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return {}
    
    def find_pages_for_section(self, section_num):
        """Find pages containing a section"""
        try:
            with open(self.raw_text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pages_found = []
            page_num = 1
            
            while True:
                page_start = f"=== PAGE {page_num} ==="
                page_end = f"=== PAGE {page_num + 1} ==="
                
                start_idx = content.find(page_start)
                if start_idx == -1:
                    break
                
                end_idx = content.find(page_end)
                if end_idx == -1:
                    page_content = content[start_idx:]
                else:
                    page_content = content[start_idx:end_idx]
                
                # Check if section appears as a HEADING on this page (at start of line)
                if re.search(rf'(?m)^{re.escape(section_num)}\b', page_content):
                    pages_found.append(page_num)
                
                page_num += 1
                if page_num > 1000: # Scan up to 1000 pages
                    break
            
            return pages_found
            
        except Exception as e:
            print(f"Error finding pages: {e}")
            return []
    
    def format_page_range(self, pages):
        """Convert page list to range format"""
        if not pages:
            return ""
        
        pages = sorted(set(pages))  # Remove duplicates and sort
        
        if len(pages) == 1:
            return str(pages[0])
        
        # Group consecutive pages
        ranges = []
        start = pages[0]
        end = pages[0]
        
        for page in pages[1:]:
            if page == end + 1:
                end = page
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = page
                end = page
        
        # Add last range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        
        return ", ".join(ranges)
    
    def generate_hierarchical_index(self):
        """Generate index with proper hierarchy"""
        topics = self.extract_all_topics()
        
        if not topics:
            return "Could not generate index"
        
        # Sort by section number
        sorted_sections = sorted(topics.keys(), 
                                key=lambda x: [int(n) for n in x.split('.')])
        
        # Build hierarchical structure
        result = "# 📚 COMPLETE TOPIC-WISE INDEX\n\n"
        result += "| Section | Topic | Pages |\n"
        result += "|---------|-------|-------|\n"
        
        for section_num in sorted_sections:
            title = topics[section_num]
            pages = self.find_pages_for_section(section_num)
            page_range = self.format_page_range(pages)
            
            # Count dots to determine hierarchy level
            dot_count = section_num.count('.')
            
            # Indent subtopics
            if dot_count == 1:
                # Main topic (e.g., 2.1, 2.8)
                result += f"| **{section_num}** | **{title}** | **{page_range}** |\n"
            elif dot_count == 2:
                # Subtopic (e.g., 2.1.1, 2.2.1)
                result += f"| &nbsp;&nbsp;{section_num} | {title} | {page_range} |\n"
            elif dot_count == 3:
                # Sub-subtopic (if any)
                result += f"| &nbsp;&nbsp;&nbsp;&nbsp;{section_num} | {title} | {page_range} |\n"
            else:
                result += f"| {section_num} | {title} | {page_range} |\n"
        
        return result
    
    def generate_clean_text_index(self):
        """Generate index as clean hierarchical text"""
        topics = self.extract_all_topics()
        
        if not topics:
            return "Could not generate index"
        
        sorted_sections = sorted(topics.keys(), 
                                key=lambda x: [int(n) for n in x.split('.')])
        
        result = "# 📚 FILE HANDLING IN PYTHON - COMPLETE INDEX\n\n"
        
        current_main = None
        
        for section_num in sorted_sections:
            title = topics[section_num]
            pages = self.find_pages_for_section(section_num)
            page_range = self.format_page_range(pages)
            
            dot_count = section_num.count('.')
            
            # Extract main section (2.1, 2.2, 2.3, etc.)
            main_section = '.'.join(section_num.split('.')[:2])
            
            # Add chapter heading if main section changed
            if main_section != current_main:
                current_main = main_section
                result += f"\n## Chapter {main_section}\n"
            
            # Format based on hierarchy
            if dot_count == 1:
                # Main topic
                result += f"\n### {section_num} - {title}\n"
                result += f"**Pages:** {page_range}\n"
            elif dot_count == 2:
                # Subtopic
                result += f"- **{section_num}** - {title} (p. {page_range})\n"
            elif dot_count == 3:
                # Sub-subtopic
                result += f"  - {section_num} - {title} (p. {page_range})\n"
        
        return result


# Standalone functions for API
def generate_hierarchical_index(pdf_name):
    """Generate hierarchical topic index"""
    base_name = pdf_name.replace('.pdf', '')
    raw_text_file = f"documents/{base_name}_RAW_TEXT.txt"
    
    if not Path(raw_text_file).exists():
        return f"❌ RAW_TEXT file not found: {raw_text_file}"
    
    generator = HierarchicalIndexGenerator(raw_text_file)
    return generator.generate_hierarchical_index()


def generate_clean_text_index(pdf_name):
    """Generate clean text index"""
    base_name = pdf_name.replace('.pdf', '')
    raw_text_file = f"documents/{base_name}_RAW_TEXT.txt"
    
    if not Path(raw_text_file).exists():
        return f"❌ RAW_TEXT file not found: {raw_text_file}"
    
    generator = HierarchicalIndexGenerator(raw_text_file)
    return generator.generate_clean_text_index()


if __name__ == "__main__":
    import sys
    pdf = "computer 12ch2.pdf"
    if len(sys.argv) > 1:
        pdf = sys.argv[1]
    
    print("=" * 60)
    print(f"TEST: Hierarchical Index for {pdf}")
    print("=" * 60)
    print(generate_hierarchical_index(pdf))
