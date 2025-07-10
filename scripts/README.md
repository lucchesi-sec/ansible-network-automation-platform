# Documentation Link Validation System

Automated link validation system to prevent documentation link crises and maintain documentation quality.

## Overview

This system provides automated validation of internal links in documentation files to prevent broken links and maintain documentation integrity.

## Features

- **Internal Link Validation**: Validates all internal file references
- **External Link Detection**: Identifies external links for manual review
- **Multiple File Formats**: Supports Markdown (.md), ReStructuredText (.rst), and text (.txt)
- **Automated Reporting**: Generates detailed validation reports
- **CI/CD Integration**: GitHub Actions for continuous validation
- **Pre-commit Hooks**: Prevents commits with broken links
- **Multiple Output Formats**: Text and GitHub-friendly formats

## Quick Start

### Basic Validation
```bash
# Validate all documentation links
python scripts/validate_links.py

# Validate specific directory
python scripts/validate_links.py --directory docs/

# Generate report file
python scripts/validate_links.py --output validation_report.md

# Quiet mode (errors only)
python scripts/validate_links.py --quiet
```

### Setup Automation
```bash
# Set up GitHub Actions and pre-commit hooks
python scripts/validate_links.py --setup-automation
```

## Usage Examples

### Command Line Options

| Option | Description |
|--------|-------------|
| `--directory, -d` | Directory to scan (default: current) |
| `--format` | Output format: text or github |
| `--output, -o` | Output file for report |
| `--quiet, -q` | Suppress non-error output |
| `--exit-code` | Exit with non-zero code if broken links found |
| `--setup-automation` | Set up GitHub Action and pre-commit hook |

### Example Commands

```bash
# Basic validation with report
python scripts/validate_links.py --output docs_validation.md

# CI/CD mode (exit code on failure)
python scripts/validate_links.py --quiet --exit-code

# GitHub Actions format
python scripts/validate_links.py --format github --output validation_report.md
```

## Validation Rules

### Internal Links
- ✅ **Valid**: Links to existing files and directories
- ✅ **Valid**: Relative paths (./file.md, ../directory/)
- ✅ **Valid**: Anchor links to existing files (#section)
- ❌ **Invalid**: Links to non-existent files
- ❌ **Invalid**: Broken relative paths

### External Links
- ⚠️ **Warning**: HTTP/HTTPS links (manual verification recommended)
- ✅ **Ignored**: mailto:, tel:, javascript: links

### File Types Validated
- Markdown files (*.md)
- ReStructuredText files (*.rst)
- Text files (*.txt)

## Automation Setup

### GitHub Actions
Automatically validates links on:
- Push to documentation files
- Pull requests affecting documentation
- Daily scheduled runs (2 AM UTC)

**Setup**: Run `python scripts/validate_links.py --setup-automation`

### Pre-commit Hooks
Validates links before each commit to prevent broken links from entering the repository.

**Features**:
- Only validates staged documentation files
- Provides clear error messages
- Can be bypassed with `--no-verify` if needed

## Report Format

### Summary Section
```
## Summary
- **Files Scanned**: 25
- **Valid Links**: 142
- **Broken Links**: 3
- **Warnings**: 8

❌ **STATUS**: Broken links found - immediate attention required
```

### Broken Links Section
```
## 🚨 Broken Links (CRITICAL)

**File**: `docs/architecture/README.md`
**Line**: 45
**Text**: Network Design Guide
**URL**: `../network/design.md`
**Issue**: Internal link target not found
```

### Warnings Section
```
## ⚠️ Warnings

### External Links (Manual Verification Recommended)
- `README.md:12` - https://example.com/docs
- `docs/setup.md:34` - https://github.com/project/repo
```

## Integration with CI/CD

### GitHub Actions Integration
The validation runs automatically and:
- ✅ **Success**: Links are valid, workflow passes
- ❌ **Failure**: Broken links found, workflow fails
- 📋 **Artifacts**: Validation report uploaded for review
- 💬 **PR Comments**: Automatic comments on failed validations

### Pre-commit Integration
```bash
# Normal commit (validation runs automatically)
git commit -m "Update documentation"

# Skip validation if needed
git commit --no-verify -m "WIP: Documentation update"
```

## Troubleshooting

### Common Issues

#### "File not found" errors
- Check relative path syntax (use `./` for current directory)
- Verify file exists at the specified location
- Check for typos in filenames

#### Permission errors
- Ensure script has execute permissions: `chmod +x scripts/validate_links.py`
- Verify read access to all documentation directories

#### Pre-commit hook not running
- Check hook is executable: `ls -la .git/hooks/pre-commit`
- Re-run setup: `python scripts/validate_links.py --setup-automation`

### False Positives
If validation reports false positives:
1. Check if the file actually exists
2. Verify the relative path is correct
3. Test the link manually in your documentation viewer

## Maintenance

### Updating the Validator
- Update the script by modifying `scripts/validate_links.py`
- Test changes: `python scripts/validate_links.py --directory docs/`
- Commit changes to update automation

### Performance Considerations
- Validation time scales with number of files and links
- Large repositories may need timeout adjustments
- Consider excluding non-documentation directories

## Best Practices

### Writing Documentation
1. **Use relative paths**: `./file.md` instead of absolute paths
2. **Test links manually**: Verify links work in your editor
3. **Keep structure simple**: Avoid deeply nested directory structures
4. **Use consistent naming**: Follow established file naming conventions

### Maintenance Workflow
1. **Daily validation**: Review automated reports
2. **Pre-commit validation**: Fix issues before committing
3. **Pull request validation**: Ensure PR doesn't introduce broken links
4. **Regular audits**: Monthly review of external links

---

**Last Updated**: July 10, 2025  
**Maintainer**: Infrastructure Team  
**Status**: Production Ready