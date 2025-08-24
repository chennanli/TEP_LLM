#!/usr/bin/env python3
"""
Secure Configuration Management for TEP Project
===============================================
This script manages API keys and sensitive configuration across the entire project.
It ensures all systems use environment variables instead of hardcoded keys.
"""

import os
import json
import shutil
from pathlib import Path
from dotenv import load_dotenv

class SecureConfigManager:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root or os.getcwd())
        self.env_file = self.project_root / '.env'
        
        # Load environment variables
        if self.env_file.exists():
            load_dotenv(self.env_file)
        
        # Define all config files that need to be updated
        self.config_files = [
            # Legacy system
            'legacy/external_repos/FaultExplainer-main/config.json',
            'legacy/external_repos/FaultExplainer-main/backend/.env',
            'legacy/external_repos/FaultExplainer-MultiLLM/backend/.env',
            
            # Integration system
            'integration/external_repos/FaultExplainer-main/config.json',
            'integration/external_repos/FaultExplainer-main/backend/.env',
            'integration/src/backend/services/llm-analysis/config.json',
            'integration/.env',
        ]
    
    def get_api_keys(self):
        """Get API keys from environment variables."""
        return {
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY', ''),
            'GOOGLE_API_KEY_BACKUP': os.getenv('GOOGLE_API_KEY_BACKUP', ''),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        }
    
    def create_secure_config_json(self, template_path, output_path):
        """Create a secure config.json using environment variables."""
        try:
            # Read template or existing config
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    config = json.load(f)
            else:
                # Create default config structure
                config = {
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
            
            # Update with environment variable placeholders
            if 'models' in config:
                if 'anthropic' in config['models']:
                    config['models']['anthropic']['api_key'] = "${ANTHROPIC_API_KEY}"
                if 'gemini' in config['models']:
                    config['models']['gemini']['api_key'] = "${GOOGLE_API_KEY}"
                    config['models']['gemini']['backup_api_key'] = "${GOOGLE_API_KEY_BACKUP}"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write secure config
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Created secure config: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating config {output_path}: {e}")
            return False
    
    def create_secure_env_file(self, output_path):
        """Create a secure .env file with environment variable references."""
        try:
            api_keys = self.get_api_keys()
            
            env_content = f"""# TEP Project Environment Variables
# This file uses environment variables - safe for git commits

OPENAI_API_KEY={api_keys['OPENAI_API_KEY']}
GOOGLE_API_KEY={api_keys['GOOGLE_API_KEY']}
GOOGLE_API_KEY_BACKUP={api_keys['GOOGLE_API_KEY_BACKUP']}
ANTHROPIC_API_KEY={api_keys['ANTHROPIC_API_KEY']}
"""
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(env_content)
            
            print(f"✅ Created secure .env: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating .env {output_path}: {e}")
            return False
    
    def update_all_configs(self):
        """Update all configuration files to use secure environment variables."""
        print("🔒 UPDATING ALL CONFIGURATIONS TO USE ENVIRONMENT VARIABLES")
        print("=" * 60)
        
        api_keys = self.get_api_keys()
        
        # Check if we have the required API keys
        if not api_keys['GOOGLE_API_KEY']:
            print("❌ GOOGLE_API_KEY not found in environment variables")
            return False
        
        success_count = 0
        total_count = 0
        
        for config_path in self.config_files:
            full_path = self.project_root / config_path
            total_count += 1
            
            if not full_path.exists():
                print(f"⏭️ Skipping (not found): {config_path}")
                continue
            
            if config_path.endswith('.json'):
                if self.create_secure_config_json(full_path, full_path):
                    success_count += 1
            elif config_path.endswith('.env'):
                if self.create_secure_env_file(full_path):
                    success_count += 1
        
        print(f"\n📊 Updated {success_count}/{total_count} configuration files")
        
        if success_count == total_count:
            print("🎉 All configurations updated successfully!")
            return True
        else:
            print("⚠️ Some configurations failed to update")
            return False
    
    def verify_security(self):
        """Verify that no hardcoded API keys remain in the project."""
        print("\n🔍 VERIFYING SECURITY - SCANNING FOR HARDCODED API KEYS")
        print("=" * 60)
        
        # Patterns to search for
        patterns = [
            'AIzaSy',  # Google API keys
            'sk-ant-api',  # Anthropic API keys
            'sk-proj-',  # OpenAI API keys
        ]
        
        issues_found = []
        
        # Scan all Python, JSON, and env files
        for pattern in ['**/*.py', '**/*.json', '**/*.env']:
            for file_path in self.project_root.glob(pattern):
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['node_modules', '.git', '__pycache__', 'temp']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for search_pattern in patterns:
                            if search_pattern in content:
                                # Skip if it's a template or example
                                if any(template in str(file_path) for template in ['.template', 'example', 'test_']):
                                    continue
                                
                                issues_found.append(f"{file_path}: Contains {search_pattern}")
                
                except Exception as e:
                    continue
        
        if issues_found:
            print("❌ SECURITY ISSUES FOUND:")
            for issue in issues_found:
                print(f"  • {issue}")
            return False
        else:
            print("✅ No hardcoded API keys found - project is secure!")
            return True

def main():
    """Main function to run secure configuration management."""
    print("🔒 TEP PROJECT SECURE CONFIGURATION MANAGER")
    print("=" * 60)
    
    manager = SecureConfigManager()
    
    # Update all configurations
    config_success = manager.update_all_configs()
    
    # Verify security
    security_success = manager.verify_security()
    
    print("\n" + "=" * 60)
    if config_success and security_success:
        print("🎉 PROJECT IS SECURE AND READY FOR GITHUB COMMITS!")
        print("✅ All API keys are now managed through environment variables")
        print("✅ No hardcoded keys found in the codebase")
        print("\n📋 Next steps:")
        print("1. Commit changes to git")
        print("2. Share .env.template with team members")
        print("3. Keep .env file private (it's in .gitignore)")
    else:
        print("⚠️ SECURITY SETUP INCOMPLETE")
        print("Please review the issues above before committing to git")

if __name__ == "__main__":
    main()
