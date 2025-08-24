#!/usr/bin/env python3
"""
GitHub Cleanup Script for TEP Project
=====================================
This script prepares the project for GitHub by:
1. Removing sensitive history files
2. Creating template versions of config files
3. Ensuring no API keys are exposed
"""

import os
import json
import shutil
from pathlib import Path

def cleanup_history_files():
    """Remove .history directory and other sensitive files."""
    print("🧹 CLEANING UP SENSITIVE FILES")
    print("=" * 50)
    
    # Remove .history directory
    history_dir = Path('.history')
    if history_dir.exists():
        shutil.rmtree(history_dir)
        print("✅ Removed .history directory")
    
    # Remove other sensitive files
    sensitive_patterns = [
        '**/*api_key*',
        '**/*secret*',
        '**/*credential*',
        '**/temp_*',
        '**/*_backup_*',
    ]
    
    removed_count = 0
    for pattern in sensitive_patterns:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file() and not any(keep in str(file_path) for keep in ['template', 'example']):
                file_path.unlink()
                print(f"✅ Removed: {file_path}")
                removed_count += 1
    
    print(f"📊 Removed {removed_count} sensitive files")

def create_config_templates():
    """Create template versions of config files."""
    print("\n📋 CREATING CONFIG TEMPLATES")
    print("=" * 50)
    
    # Template config.json structure
    template_config = {
        "models": {
            "anthropic": {
                "api_key": "${ANTHROPIC_API_KEY}",
                "model_name": "claude-3-5-sonnet-20241022",
                "enabled": False,
                "premium": True,
                "description": "High-quality analysis with API costs"
            },
            "gemini": {
                "api_key": "${GOOGLE_API_KEY}",
                "backup_api_key": "${GOOGLE_API_KEY_BACKUP}",
                "model_name": "gemini-1.5-flash",
                "enabled": True,
                "premium": True,
                "description": "Primary LLM for TEP fault analysis",
                "auto_failover": True
            },
            "lmstudio": {
                "enabled": False,
                "base_url": "http://127.0.0.1:1234/v1",
                "model_name": "mistralai_mistral-small-3.1-24b-instruct-2503",
                "api_key": "not-needed",
                "premium": False,
                "description": "Local model - no API costs"
            }
        }
    }
    
    # Template .env content
    template_env = """# TEP Project Environment Variables Template
# Copy this file to .env and fill in your actual API keys
# DO NOT commit .env to git - it's in .gitignore

# OpenAI API Key (if needed)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Keys
GOOGLE_API_KEY=your_primary_gemini_api_key_here
GOOGLE_API_KEY_BACKUP=your_backup_gemini_api_key_here

# Anthropic Claude API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LMStudio Configuration (local)
LMSTUDIO_BASE_URL=http://127.0.0.1:1234/v1
LMSTUDIO_MODEL_NAME=mistralai_mistral-small-3.1-24b-instruct-2503
"""
    
    # Create templates in key locations
    template_locations = [
        'config.template.json',
        'legacy/external_repos/FaultExplainer-main/config.template.json',
        'integration/external_repos/FaultExplainer-main/config.template.json',
        'integration/src/backend/services/llm-analysis/config.template.json',
    ]
    
    for location in template_locations:
        try:
            os.makedirs(os.path.dirname(location), exist_ok=True)
            with open(location, 'w') as f:
                json.dump(template_config, f, indent=2)
            print(f"✅ Created: {location}")
        except Exception as e:
            print(f"❌ Failed to create {location}: {e}")
    
    # Create .env.template if it doesn't exist
    if not os.path.exists('.env.template'):
        with open('.env.template', 'w') as f:
            f.write(template_env)
        print("✅ Created: .env.template")

def verify_github_ready():
    """Verify the project is ready for GitHub."""
    print("\n🔍 VERIFYING GITHUB READINESS")
    print("=" * 50)
    
    # Check for sensitive patterns
    sensitive_patterns = ['AIzaSy', 'sk-ant-api', 'sk-proj-']
    issues = []
    
    # Only scan files that would be committed to git
    for pattern in ['**/*.py', '**/*.json', '**/*.md', '**/*.js', '**/*.ts']:
        for file_path in Path('.').glob(pattern):
            # Skip files that are in .gitignore
            if any(skip in str(file_path) for skip in [
                '.history', 'node_modules', '__pycache__', '.git', 
                'temp', '.env', 'scripts/cleanup_for_github.py',
                'scripts/secure_config.py'
            ]):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for pattern in sensitive_patterns:
                        if pattern in content and 'template' not in str(file_path):
                            issues.append(f"{file_path}: Contains {pattern}")
            except:
                continue
    
    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues[:10]:  # Show first 10 issues
            print(f"  • {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
        return False
    else:
        print("✅ No sensitive data found in files that would be committed!")
        return True

def create_github_readme():
    """Create a README section about API key management."""
    readme_section = """
## 🔐 API Key Management

This project uses environment variables to manage API keys securely:

### Setup Instructions:
1. Copy `.env.template` to `.env`
2. Fill in your actual API keys in `.env`
3. Never commit `.env` to git (it's in .gitignore)

### Supported APIs:
- **Google Gemini**: Primary LLM for fault analysis
- **Anthropic Claude**: Backup LLM option
- **OpenAI**: Optional additional LLM
- **LMStudio**: Local model option (no API key needed)

### Configuration Files:
All `config.json` files use environment variable placeholders like `${GOOGLE_API_KEY}` which are automatically resolved at runtime.

### Security:
- ✅ No hardcoded API keys in the repository
- ✅ All sensitive data in `.env` (gitignored)
- ✅ Template files provided for easy setup
- ✅ Automatic environment variable resolution
"""
    
    print("\n📝 GITHUB README SECTION")
    print("=" * 50)
    print("Add this section to your README.md:")
    print(readme_section)

def main():
    """Main cleanup function."""
    print("🧹 TEP PROJECT GITHUB CLEANUP")
    print("=" * 60)
    
    # Step 1: Clean up sensitive files
    cleanup_history_files()
    
    # Step 2: Create templates
    create_config_templates()
    
    # Step 3: Verify readiness
    github_ready = verify_github_ready()
    
    # Step 4: Show README section
    create_github_readme()
    
    print("\n" + "=" * 60)
    if github_ready:
        print("🎉 PROJECT IS READY FOR GITHUB!")
        print("✅ All sensitive files cleaned up")
        print("✅ Template files created")
        print("✅ No API keys in committed files")
        print("\n📋 Next steps:")
        print("1. Review the changes")
        print("2. Add the README section above")
        print("3. Commit to git")
        print("4. Push to GitHub")
    else:
        print("⚠️ PROJECT NEEDS MORE CLEANUP")
        print("Please fix the issues above before committing")

if __name__ == "__main__":
    main()
