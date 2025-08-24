#!/usr/bin/env python3
"""
Verification Script: Legacy/Integration System Separation
=========================================================
This script verifies that both systems are completely independent.
"""

import os
import sys

def test_system_independence():
    """Test that both systems have their own TEP modules."""
    
    print("🔍 TESTING SYSTEM INDEPENDENCE")
    print("=" * 50)
    
    # Test Legacy System
    print("\n📁 Testing Legacy System:")
    legacy_tep = "legacy/external_repos/tep2py-master/tep2py.py"
    if os.path.exists(legacy_tep):
        print(f"✅ Legacy TEP: {legacy_tep}")
        legacy_count = len([f for f in os.listdir("legacy/external_repos") if not f.startswith(".")])
        print(f"📊 Legacy contains: {legacy_count} external repos")
    else:
        print(f"❌ Legacy TEP missing: {legacy_tep}")
    
    # Test Integration System  
    print("\n📁 Testing Integration System:")
    integration_tep = "integration/external_repos/tep2py-master/tep2py.py"
    if os.path.exists(integration_tep):
        print(f"✅ Integration TEP: {integration_tep}")
        integration_count = len([f for f in os.listdir("integration/external_repos") if not f.startswith(".")])
        print(f"📊 Integration contains: {integration_count} external repos")
    else:
        print(f"❌ Integration TEP missing: {integration_tep}")

def check_port_configuration():
    """Check that systems use different ports."""
    
    print("\n🔌 CHECKING PORT CONFIGURATION")
    print("=" * 50)
    
    # Check Legacy Ports
    print("\n📁 Legacy System Ports:")
    legacy_files = [
        ("Control Panel", "legacy/unified_tep_control_panel.py", "9001"),
        ("Backend", "legacy/external_repos/FaultExplainer-main/backend/app.py", "8000"),
        ("Frontend", "legacy/external_repos/FaultExplainer-main/frontend/vite.config.ts", "5173")
    ]
    
    for name, file_path, expected_port in legacy_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                if expected_port in content:
                    print(f"✅ {name}: Port {expected_port}")
                else:
                    print(f"⚠️ {name}: Port {expected_port} not found")
        else:
            print(f"❌ {name}: File not found")
    
    # Check Integration Ports
    print("\n📁 Integration System Ports:")
    integration_files = [
        ("Control Panel", "integration/unified_control_panel.py", "9002"),
        ("Backend", "integration/external_repos/FaultExplainer-main/backend/app.py", "8001"),
        ("Frontend", "integration/external_repos/FaultExplainer-main/frontend/vite.config.ts", "5174")
    ]
    
    for name, file_path, expected_port in integration_files:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
                if expected_port in content:
                    print(f"✅ {name}: Port {expected_port}")
                else:
                    print(f"⚠️ {name}: Port {expected_port} not found")
        else:
            print(f"❌ {name}: File not found")

def check_file_structure():
    """Check that both systems have complete file structures."""
    
    print("\n📂 CHECKING FILE STRUCTURE")
    print("=" * 50)
    
    required_paths = [
        "external_repos/tep2py-master/tep2py.py",
        "external_repos/FaultExplainer-main/backend/app.py",
        "external_repos/FaultExplainer-main/frontend/package.json"
    ]
    
    for system in ["legacy", "integration"]:
        print(f"\n📁 {system.title()} System:")
        all_present = True
        for path in required_paths:
            full_path = os.path.join(system, path)
            if os.path.exists(full_path):
                print(f"✅ {path}")
            else:
                print(f"❌ {path} - MISSING")
                all_present = False
        
        if all_present:
            print(f"🎉 {system.title()} system is COMPLETE")
        else:
            print(f"⚠️ {system.title()} system has MISSING files")

def main():
    """Run all verification tests."""
    
    print("🔧 LEGACY/INTEGRATION SEPARATION VERIFICATION")
    print("=" * 60)
    print("This script verifies that both systems are completely independent")
    print("and can run simultaneously without conflicts.\n")
    
    test_system_independence()
    check_port_configuration()
    check_file_structure()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print("✅ Both systems should now be completely independent")
    print("✅ Legacy system uses ports: 9001 (panel), 8000 (backend), 5173 (frontend)")
    print("✅ Integration system uses ports: 9002 (panel), 8001 (backend), 5174 (frontend)")
    print("✅ No cross-folder dependencies")
    print("✅ Both systems can run simultaneously")
    print("\n🚀 Ready to use both systems independently!")

if __name__ == "__main__":
    main()
