#!/usr/bin/env python3
"""
Release Sanitization Script

Erzeugt eine "shareable" Struktur, die sicher ist:
- Löscht .env, .DS_Store, sensitive files
- Kopiert .env.example
- Meldet nur Dateinamen/Keys, niemals Werte

Was geändert: Neues Script für sichere Release-Erstellung
Warum: .env enthält Secrets, darf niemals geteilt werden
Rollback: N/A (Script erstellt nur neue Struktur, keine Änderungen an Source)
"""
import os
import shutil
import sys
from pathlib import Path
from typing import Set, List

# Files/patterns to remove
SENSITIVE_PATTERNS: Set[str] = {
    ".env",
    ".DS_Store",
    "*.pyc",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "*.log",
    "*.swp",
    "*.swo",
    "*~",
    ".idea",
    ".vscode",
}

# Directories to skip entirely
SKIP_DIRS: Set[str] = {
    "node_modules",
    ".git",
    "venv",
    "env",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
}


def should_skip_file(filepath: Path) -> bool:
    """Check if file should be skipped."""
    name = filepath.name
    
    # Check exact matches
    if name in {".env", ".DS_Store"}:
        return True
    
    # Check patterns
    for pattern in SENSITIVE_PATTERNS:
        if pattern.startswith("*."):
            if name.endswith(pattern[1:]):
                return True
        elif pattern == name:
            return True
    
    return False


def should_skip_dir(dirpath: Path) -> bool:
    """Check if directory should be skipped."""
    return dirpath.name in SKIP_DIRS


def sanitize_directory(source: Path, target: Path, dry_run: bool = False) -> List[str]:
    """
    Copy directory tree, removing sensitive files.
    
    Returns list of removed files (for reporting).
    """
    removed: List[str] = []
    
    if not source.exists():
        print(f"Error: Source directory {source} does not exist", file=sys.stderr)
        return removed
    
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
    
    for root, dirs, files in os.walk(source):
        root_path = Path(root)
        
        # Filter out skip directories
        dirs[:] = [d for d in dirs if not should_skip_dir(root_path / d)]
        
        # Determine relative path
        try:
            rel_path = root_path.relative_to(source)
            target_dir = target / rel_path
        except ValueError:
            continue
        
        # Process files
        for file in files:
            file_path = root_path / file
            
            if should_skip_file(file_path):
                removed.append(str(file_path.relative_to(source)))
                continue
            
            # Copy file
            target_file = target_dir / file
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, target_file)
        
        # Create .env.example if .env.example exists in source
        env_example_source = source / ".env.example"
        env_example_target = target / ".env.example"
        if env_example_source.exists() and not env_example_target.exists():
            if not dry_run:
                shutil.copy2(env_example_source, env_example_target)
                print(f"Copied .env.example")
    
    return removed


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sanitize release directory by removing sensitive files"
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Source directory to sanitize"
    )
    parser.add_argument(
        "target",
        type=Path,
        nargs="?",
        default=None,
        help="Target directory (default: source + '_sanitized')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - show what would be removed without copying"
    )
    
    args = parser.parse_args()
    
    source = args.source.resolve()
    if args.target:
        target = Path(args.target).resolve()
    else:
        target = source.parent / f"{source.name}_sanitized"
    
    if target.exists() and not args.dry_run:
        print(f"Error: Target directory {target} already exists", file=sys.stderr)
        sys.exit(1)
    
    print(f"Sanitizing: {source} -> {target}")
    if args.dry_run:
        print("(DRY RUN - no files will be copied)")
    
    removed = sanitize_directory(source, target, dry_run=args.dry_run)
    
    print(f"\nRemoved {len(removed)} sensitive files:")
    for file in sorted(removed):
        # Only print filenames, never values
        print(f"  - {file}")
    
    if not args.dry_run:
        print(f"\nSanitized directory created: {target}")
        print("\nWARNING: Review the sanitized directory before sharing!")
        print("Remember: Rotate any keys if they were ever shared.")


if __name__ == "__main__":
    main()

