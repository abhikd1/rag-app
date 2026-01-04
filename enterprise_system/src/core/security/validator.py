"""
Input validation and sanitization layer.
Prevents injection attacks and malformed inputs.
"""

import re
from typing import Optional


class InputValidator:
    """Validates and sanitizes user inputs"""
    
    # Maximum query length to prevent DoS
    MAX_QUERY_LENGTH = 10000
    
    # Patterns that might indicate injection attempts
    SUSPICIOUS_PATTERNS = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
    ]
    
    @classmethod
    def validate_query(cls, query: str) -> tuple[bool, Optional[str]]:
        """
        Validates a user query.
        
        Args:
            query: User input string
            
        Returns:
            (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        if len(query) > cls.MAX_QUERY_LENGTH:
            return False, f"Query exceeds maximum length of {cls.MAX_QUERY_LENGTH} characters"
        
        # Check for suspicious patterns
        query_lower = query.lower()
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if re.search(pattern, query_lower):
                return False, f"Query contains suspicious pattern: {pattern}"
        
        return True, None
    
    @classmethod
    def sanitize_query(cls, query: str) -> str:
        """
        Sanitizes a query by removing potentially harmful content.
        
        Args:
            query: Raw user input
            
        Returns:
            Sanitized query string
        """
        # Remove null bytes
        query = query.replace('\x00', '')
        
        # Normalize whitespace
        query = ' '.join(query.split())
        
        # Strip leading/trailing whitespace
        query = query.strip()
        
        return query
    
    @classmethod
    def validate_and_sanitize(cls, query: str) -> tuple[bool, str, Optional[str]]:
        """
        Combined validation and sanitization.
        
        Returns:
            (is_valid, sanitized_query, error_message)
        """
        sanitized = cls.sanitize_query(query)
        is_valid, error = cls.validate_query(sanitized)
        return is_valid, sanitized, error
