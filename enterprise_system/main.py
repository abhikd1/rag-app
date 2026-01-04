"""
Main entry point for the Enterprise Study System.
Run this file to start the application.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interface.cli.app import main

if __name__ == "__main__":
    main()
