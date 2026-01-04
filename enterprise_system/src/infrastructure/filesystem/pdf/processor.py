"""
PDF Processing Infrastructure.
Handles extraction, heading detection, and indexing of PDF documents.
"""

import fitz  # PyMuPDF
import re
from typing import List, Tuple, Optional
from dataclasses import dataclass
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from src.core.logging.logger import LoggerFactory


@dataclass
class PageContent:
    """Represents content from a single page"""
    page_number: int
    text: str
    headings: List[str]
    is_blank: bool = False


@dataclass
class HeadingInfo:
    """Information about a detected heading"""
    text: str
    page_number: int
    line_number: int
    level: int  # 1 = Chapter, 2 = Section, 3 = Subsection


class PDFProcessor:
    """
    Processes PDF files with advanced features:
    - Text extraction
    - Heading detection
    - Structure analysis
    - Page-by-page indexing
    """
    
    # Patterns for detecting headings
    CHAPTER_PATTERNS = [
        r'^Chapter \d+',
        r'^CHAPTER \d+',
        r'^Part [IVX]+',
        r'^PART [IVX]+',
    ]
    
    SECTION_PATTERNS = [
        r'^\d+\.\s+[A-Z]',  # "1. Introduction"
        r'^\d+\.\d+\s+',    # "1.1 Background"
    ]
    
    def __init__(self):
        self.logger = LoggerFactory.get_logger(__name__)
    
    def detect_heading(self, text: str, font_size: Optional[float] = None) -> Tuple[bool, int]:
        """
        Detect if a line is a heading and determine its level.
        
        Args:
            text: Line of text to analyze
            font_size: Optional font size information
            
        Returns:
            (is_heading, level) where level is 1-3
        """
        text = text.strip()
        
        if not text or len(text) > 150:
            return False, 0
        
        # Check for chapter-level headings
        for pattern in self.CHAPTER_PATTERNS:
            if re.match(pattern, text):
                return True, 1
        
        # Check for section-level headings
        for pattern in self.SECTION_PATTERNS:
            if re.match(pattern, text):
                return True, 2
        
        # All caps and short = likely heading
        if text.isupper() and len(text) < 80:
            return True, 3
        
        return False, 0
    
    def extract_page(self, pdf_path: str, page_num: int) -> PageContent:
        """
        Extract content from a specific page.
        
        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)
            
        Returns:
            PageContent object
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Detect headings in this page
            headings = []
            if text.strip():
                lines = text.split('\n')
                for line_num, line in enumerate(lines, 1):
                    is_heading, level = self.detect_heading(line)
                    if is_heading:
                        headings.append(line.strip())
            
            return PageContent(
                page_number=page_num + 1,  # 1-indexed for user display
                text=text,
                headings=headings,
                is_blank=not text.strip()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to extract page {page_num}: {e}")
            return PageContent(
                page_number=page_num + 1,
                text="",
                headings=[],
                is_blank=True
            )
    
    def extract_all_pages(self, pdf_path: str) -> List[PageContent]:
        """
        Extract all pages from a PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of PageContent objects
        """
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            self.logger.info(f"Extracting {total_pages} pages from {pdf_path}")
            
            pages = []
            for page_num in range(total_pages):
                page_content = self.extract_page(pdf_path, page_num)
                pages.append(page_content)
                
                if (page_num + 1) % 10 == 0:
                    self.logger.info(f"Processed {page_num + 1}/{total_pages} pages")
            
            self.logger.info(f"Extraction complete: {total_pages} pages")
            return pages
            
        except Exception as e:
            self.logger.error(f"Failed to process PDF: {e}")
            return []
    
    def generate_index(self, pages: List[PageContent]) -> List[HeadingInfo]:
        """
        Generate an index of all headings in the document.
        
        Args:
            pages: List of PageContent objects
            
        Returns:
            List of HeadingInfo objects
        """
        index = []
        
        for page in pages:
            for heading in page.headings:
                is_heading, level = self.detect_heading(heading)
                if is_heading:
                    index.append(HeadingInfo(
                        text=heading,
                        page_number=page.page_number,
                        line_number=0,  # Would need more detailed parsing
                        level=level
                    ))
        
        return index
