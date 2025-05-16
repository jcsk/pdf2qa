#!/usr/bin/env python3
"""
Script to index the codebase, excluding dependency files and other artifacts.
This can be used to generate a list of files for documentation or analysis.
"""

import os
import sys
from pathlib import Path


def should_ignore(path, ignore_patterns):
    """Check if a path should be ignored based on patterns."""
    path_str = str(path)
    for pattern in ignore_patterns:
        if pattern in path_str:
            return True
    return False


def index_codebase(root_dir='.', output_file=None, ignore_patterns=None):
    """
    Index the codebase, excluding files matching ignore patterns.
    
    Args:
        root_dir: Root directory to start indexing from.
        output_file: Optional file to write the index to.
        ignore_patterns: List of patterns to ignore.
    
    Returns:
        List of file paths.
    """
    if ignore_patterns is None:
        ignore_patterns = [
            '.venv/', 
            '__pycache__/', 
            '.git/',
            '.pytest_cache/',
            '.DS_Store',
            '.egg-info',
            'dist/',
            'build/',
        ]
    
    root_path = Path(root_dir).resolve()
    files = []
    
    for path in root_path.glob('**/*'):
        if path.is_file() and not should_ignore(path, ignore_patterns):
            # Get relative path from root
            rel_path = path.relative_to(root_path)
            files.append(str(rel_path))
    
    # Sort files for consistent output
    files.sort()
    
    # Write to output file if specified
    if output_file:
        with open(output_file, 'w') as f:
            for file in files:
                f.write(f"{file}\n")
    
    return files


if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs('scripts', exist_ok=True)
    
    # Default output file
    output_file = 'scripts/codebase_index.txt'
    
    # Allow specifying output file as command line argument
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    # Index the codebase
    files = index_codebase(output_file=output_file)
    
    print(f"Indexed {len(files)} files. Output written to {output_file}")
