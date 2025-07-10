#!/usr/bin/env python3
"""
Documentation Link Validator
Automated link validation system to prevent documentation link crises.
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple
import urllib.parse
from collections import defaultdict


class LinkValidator:
    """Validates internal and external links in documentation files."""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir).resolve()
        self.markdown_files: List[Path] = []
        self.broken_links: List[Dict] = []
        self.valid_links: List[Dict] = []
        self.warnings: List[Dict] = []
        
        # Link patterns
        self.markdown_link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
        self.reference_link_pattern = re.compile(r'\[([^\]]*)\]:\s*(.+)')
        
        # File extensions to validate
        self.valid_extensions = {'.md', '.txt', '.rst'}
        
    def find_markdown_files(self) -> None:
        """Find all markdown files in the directory tree."""
        for root, _, files in os.walk(self.base_dir):
            for file in files:
                if any(file.endswith(ext) for ext in self.valid_extensions):
                    self.markdown_files.append(Path(root) / file)
    
    def extract_links(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Extract all links from a markdown file."""
        links = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find markdown-style links [text](url)
            for line_num, line in enumerate(content.splitlines(), 1):
                # Markdown links
                for match in self.markdown_link_pattern.finditer(line):
                    text, url = match.groups()
                    links.append((text, url, line_num))
                
                # Reference links
                for match in self.reference_link_pattern.finditer(line):
                    text, url = match.groups()
                    links.append((text, url.strip(), line_num))
                    
        except Exception as e:
            self.warnings.append({
                'file': str(file_path),
                'message': f"Error reading file: {e}",
                'type': 'file_error'
            })
            
        return links
    
    def validate_internal_link(self, file_path: Path, link_url: str) -> bool:
        """Validate internal file/directory links."""
        # Remove URL fragments (anchors)
        clean_url = link_url.split('#')[0]
        
        # Skip empty links or pure anchors
        if not clean_url:
            return True
            
        # Handle relative paths
        if clean_url.startswith('./'):
            clean_url = clean_url[2:]
        elif clean_url.startswith('../'):
            # Handle relative parent directory references
            target_path = file_path.parent / clean_url
        else:
            # Relative to current file directory
            target_path = file_path.parent / clean_url
            
        try:
            target_path = target_path.resolve()
            
            # Check if target exists
            if target_path.exists():
                return True
                
            # Check if it's a directory reference without trailing slash
            if (target_path.parent / target_path.name).exists():
                return True
                
        except Exception:
            pass
            
        return False
    
    def is_external_link(self, url: str) -> bool:
        """Check if a link is external (HTTP/HTTPS)."""
        return url.startswith(('http://', 'https://', 'ftp://', 'mailto:'))
    
    def validate_file(self, file_path: Path) -> None:
        """Validate all links in a single file."""
        links = self.extract_links(file_path)
        
        for text, url, line_num in links:
            link_info = {
                'file': str(file_path.relative_to(self.base_dir)),
                'text': text,
                'url': url,
                'line': line_num
            }
            
            # Skip certain link types
            if url.startswith(('mailto:', 'tel:', 'javascript:')):
                continue
                
            # Validate external links (mark for manual review)
            if self.is_external_link(url):
                link_info['type'] = 'external'
                self.warnings.append({
                    **link_info,
                    'message': 'External link - manual verification recommended',
                    'type': 'external_link'
                })
                continue
            
            # Validate internal links
            if self.validate_internal_link(file_path, url):
                link_info['type'] = 'internal_valid'
                self.valid_links.append(link_info)
            else:
                link_info['type'] = 'internal_broken'
                link_info['message'] = 'Internal link target not found'
                self.broken_links.append(link_info)
    
    def validate_all(self) -> Dict:
        """Validate all links in all markdown files."""
        self.find_markdown_files()
        
        print(f"Found {len(self.markdown_files)} documentation files to validate...")
        
        for file_path in self.markdown_files:
            self.validate_file(file_path)
        
        return {
            'total_files': len(self.markdown_files),
            'broken_links': len(self.broken_links),
            'valid_links': len(self.valid_links),
            'warnings': len(self.warnings),
            'details': {
                'broken': self.broken_links,
                'warnings': self.warnings,
                'valid': self.valid_links
            }
        }
    
    def generate_report(self, results: Dict) -> str:
        """Generate a detailed validation report."""
        report = []
        report.append("# Documentation Link Validation Report")
        report.append(f"Generated: {self.get_timestamp()}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        report.append(f"- **Files Scanned**: {results['total_files']}")
        report.append(f"- **Valid Links**: {results['valid_links']}")
        report.append(f"- **Broken Links**: {results['broken_links']}")
        report.append(f"- **Warnings**: {results['warnings']}")
        report.append("")
        
        # Status
        if results['broken_links'] == 0:
            report.append("✅ **STATUS**: All internal links are valid!")
        else:
            report.append("❌ **STATUS**: Broken links found - immediate attention required")
        report.append("")
        
        # Broken links
        if results['broken_links'] > 0:
            report.append("## 🚨 Broken Links (CRITICAL)")
            report.append("")
            for link in self.broken_links:
                report.append(f"**File**: `{link['file']}`")
                report.append(f"**Line**: {link['line']}")
                report.append(f"**Text**: {link['text']}")
                report.append(f"**URL**: `{link['url']}`")
                report.append(f"**Issue**: {link['message']}")
                report.append("")
        
        # Warnings
        if results['warnings'] > 0:
            report.append("## ⚠️ Warnings")
            report.append("")
            external_links = [w for w in self.warnings if w.get('type') == 'external_link']
            if external_links:
                report.append("### External Links (Manual Verification Recommended)")
                for warning in external_links[:10]:  # Limit to first 10
                    report.append(f"- `{warning['file']}:{warning['line']}` - {warning['url']}")
                if len(external_links) > 10:
                    report.append(f"- ... and {len(external_links) - 10} more external links")
                report.append("")
            
            other_warnings = [w for w in self.warnings if w.get('type') != 'external_link']
            if other_warnings:
                report.append("### Other Warnings")
                for warning in other_warnings:
                    report.append(f"- `{warning['file']}` - {warning['message']}")
                report.append("")
        
        # Statistics by file
        if results['broken_links'] > 0:
            report.append("## Broken Links by File")
            file_stats = defaultdict(int)
            for link in self.broken_links:
                file_stats[link['file']] += 1
            
            for file_path, count in sorted(file_stats.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- `{file_path}`: {count} broken link{'s' if count > 1 else ''}")
            report.append("")
        
        return "\n".join(report)
    
    def get_timestamp(self) -> str:
        """Get current timestamp for reports."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_github_action():
    """Create GitHub Action for automated link validation."""
    action_content = """name: Documentation Link Validation

on:
  push:
    paths:
      - '**.md'
      - '**.rst'
      - '**.txt'
      - 'docs/**'
  pull_request:
    paths:
      - '**.md'
      - '**.rst' 
      - '**.txt'
      - 'docs/**'
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

jobs:
  validate-links:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Validate documentation links
      run: |
        python scripts/validate_links.py --format github
        
    - name: Upload validation report
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: link-validation-report
        path: link_validation_report.md
        
    - name: Comment on PR
      if: failure() && github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = fs.readFileSync('link_validation_report.md', 'utf8');
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: `## 🚨 Documentation Link Validation Failed\\n\\n${report}`
          });
"""
    return action_content


def create_pre_commit_hook():
    """Create pre-commit hook for link validation."""
    hook_content = """#!/bin/bash
# Pre-commit hook for documentation link validation

echo "🔍 Validating documentation links..."

# Run link validation
if python scripts/validate_links.py --quiet --exit-code; then
    echo "✅ All documentation links are valid"
    exit 0
else
    echo "❌ Broken documentation links found!"
    echo "Please fix broken links before committing."
    echo "Run 'python scripts/validate_links.py' for detailed report."
    exit 1
fi
"""
    return hook_content


def main():
    parser = argparse.ArgumentParser(description='Validate documentation links')
    parser.add_argument('--directory', '-d', default='.', 
                      help='Directory to scan (default: current directory)')
    parser.add_argument('--format', choices=['text', 'github'], default='text',
                      help='Output format')
    parser.add_argument('--output', '-o', help='Output file for report')
    parser.add_argument('--quiet', '-q', action='store_true',
                      help='Suppress non-error output')
    parser.add_argument('--exit-code', action='store_true',
                      help='Exit with non-zero code if broken links found')
    parser.add_argument('--setup-automation', action='store_true',
                      help='Set up GitHub Action and pre-commit hook')
    
    args = parser.parse_args()
    
    # Set up automation files
    if args.setup_automation:
        # Create .github/workflows directory
        workflows_dir = Path('.github/workflows')
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Create GitHub Action
        action_file = workflows_dir / 'validate-links.yml'
        with open(action_file, 'w') as f:
            f.write(create_github_action())
        
        # Create pre-commit hook
        hooks_dir = Path('.git/hooks')
        if hooks_dir.exists():
            hook_file = hooks_dir / 'pre-commit'
            with open(hook_file, 'w') as f:
                f.write(create_pre_commit_hook())
            os.chmod(hook_file, 0o755)
            
        print("✅ Automation setup complete!")
        print("- GitHub Action: .github/workflows/validate-links.yml")
        print("- Pre-commit hook: .git/hooks/pre-commit")
        return
    
    # Run validation
    validator = LinkValidator(args.directory)
    results = validator.validate_all()
    
    # Generate report
    report = validator.generate_report(results)
    
    # Output report
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        if not args.quiet:
            print(f"Report written to: {args.output}")
    else:
        if not args.quiet:
            print(report)
    
    # Summary output
    if not args.quiet:
        print("\n" + "="*50)
        print(f"Validation Complete: {results['broken_links']} broken links found")
        if results['broken_links'] > 0:
            print("❌ CRITICAL: Fix broken links immediately")
        else:
            print("✅ SUCCESS: All links are valid")
    
    # Exit with appropriate code
    if args.exit_code and results['broken_links'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()