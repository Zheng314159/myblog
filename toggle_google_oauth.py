#!/usr/bin/env python3
"""
Toggle Google OAuth on/off by commenting/uncommenting the registration code
"""

import os
import re
import shutil
from datetime import datetime

OAUTH_FILE = "app/core/oauth.py"
BACKUP_SUFFIX = ".backup"

def backup_file():
    """Create a backup of the oauth.py file"""
    if not os.path.exists(OAUTH_FILE):
        print(f"❌ OAuth file not found: {OAUTH_FILE}")
        return False
    
    backup_file = f"{OAUTH_FILE}{BACKUP_SUFFIX}"
    shutil.copy2(OAUTH_FILE, backup_file)
    print(f"✅ Backup created: {backup_file}")
    return True

def restore_backup():
    """Restore from backup"""
    backup_file = f"{OAUTH_FILE}{BACKUP_SUFFIX}"
    if os.path.exists(backup_file):
        shutil.copy2(backup_file, OAUTH_FILE)
        print(f"✅ Restored from backup: {backup_file}")
        return True
    else:
        print(f"❌ Backup file not found: {backup_file}")
        return False

def is_google_oauth_enabled():
    """Check if Google OAuth is currently enabled"""
    try:
        with open(OAUTH_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for uncommented Google OAuth registration
        google_pattern = r'# Google OAuth\s*\nif settings\.google_client_id and settings\.google_client_secret:\s*\n\s*oauth\.register\('
        return bool(re.search(google_pattern, content, re.MULTILINE))
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def disable_google_oauth():
    """Disable Google OAuth by commenting out the registration"""
    try:
        with open(OAUTH_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match Google OAuth registration block
        pattern = r'(# Google OAuth\s*\n)(if settings\.google_client_id and settings\.google_client_secret:\s*\n\s*oauth\.register\([^)]+\)\s*\n\s*\)\s*\n)'
        
        # Replace with commented version
        replacement = r'# \1# \2'
        
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        if new_content != content:
            with open(OAUTH_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Google OAuth disabled (commented out)")
            return True
        else:
            print("⚠️  Google OAuth was already disabled or pattern not found")
            return False
            
    except Exception as e:
        print(f"❌ Error disabling Google OAuth: {e}")
        return False

def enable_google_oauth():
    """Enable Google OAuth by uncommenting the registration"""
    try:
        with open(OAUTH_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match commented Google OAuth registration block
        pattern = r'# (# Google OAuth\s*\n)(# if settings\.google_client_id and settings\.google_client_secret:\s*\n\s*# oauth\.register\([^)]+\)\s*\n\s*# \)\s*\n)'
        
        # Replace with uncommented version
        replacement = r'\1\2'
        
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        if new_content != content:
            with open(OAUTH_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Google OAuth enabled (uncommented)")
            return True
        else:
            print("⚠️  Google OAuth was already enabled or pattern not found")
            return False
            
    except Exception as e:
        print(f"❌ Error enabling Google OAuth: {e}")
        return False

def main():
    """Main function"""
    print("🔄 Google OAuth Toggle Tool")
    print("=" * 40)
    
    if not os.path.exists(OAUTH_FILE):
        print(f"❌ OAuth file not found: {OAUTH_FILE}")
        print("Please run this script from the project root directory")
        return
    
    # Check current status
    enabled = is_google_oauth_enabled()
    print(f"📊 Current status: Google OAuth is {'enabled' if enabled else 'disabled'}")
    
    # Create backup
    if not backup_file():
        return
    
    # Toggle based on current status
    if enabled:
        print("\n🔄 Disabling Google OAuth...")
        if disable_google_oauth():
            print("✅ Google OAuth has been disabled")
            print("💡 The Google login button will now be hidden due to network issues")
        else:
            print("❌ Failed to disable Google OAuth")
    else:
        print("\n🔄 Enabling Google OAuth...")
        if enable_google_oauth():
            print("✅ Google OAuth has been enabled")
            print("💡 The Google login button will be shown if network is available")
        else:
            print("❌ Failed to enable Google OAuth")
    
    print("\n" + "=" * 40)
    print("💡 Tips:")
    print("- Restart your FastAPI server after making changes")
    print("- Use the health check endpoints to verify network status")
    print("- Run 'python test_oauth_health.py' to test the endpoints")

if __name__ == "__main__":
    main() 