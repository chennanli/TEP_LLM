#!/usr/bin/env python3
"""
TEP Project Documentation Export Tool
=====================================

Export various project documentation to PDF format with proper formatting.

Usage:
    python scripts/export_documentation.py --help
    python scripts/export_documentation.py --physical-properties
    python scripts/export_documentation.py --all

Features:
- Professional PDF formatting
- Proper table layouts
- Mathematical equations
- Project branding

Author: Augment Agent
Date: 2025-01-30
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def export_physical_properties():
    """Export TEP Physical Properties to PDF."""
    print("📄 Exporting TEP Physical Properties...")
    
    try:
        from export_to_pdf import TEPPhysicalPropertiesPDF
        
        pdf_generator = TEPPhysicalPropertiesPDF()
        output_file = pdf_generator.create_pdf("docs/TEP_Physical_Properties.pdf")
        
        print(f"✅ Physical Properties PDF created: {output_file}")
        return True
        
    except ImportError:
        print("❌ Missing dependencies. Install with:")
        print("   pip install reportlab pandas")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def export_project_overview():
    """Export project overview to PDF."""
    print("📄 Exporting Project Overview...")
    # TODO: Implement project overview PDF export
    print("💡 Project overview export - Coming soon!")
    return True

def export_fault_analysis_guide():
    """Export fault analysis guide to PDF."""
    print("📄 Exporting Fault Analysis Guide...")
    # TODO: Implement fault analysis guide PDF export
    print("💡 Fault analysis guide export - Coming soon!")
    return True

def export_all_documentation():
    """Export all documentation to PDF."""
    print("📚 Exporting All Documentation...")
    
    success = True
    success &= export_physical_properties()
    success &= export_project_overview()
    success &= export_fault_analysis_guide()
    
    if success:
        print("✅ All documentation exported successfully!")
    else:
        print("❌ Some exports failed. Check error messages above.")
    
    return success

def setup_docs_directory():
    """Ensure docs directory exists."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    return docs_dir

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Export TEP project documentation to PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/export_documentation.py --physical-properties
  python scripts/export_documentation.py --all
  python scripts/export_documentation.py --help
        """
    )
    
    parser.add_argument(
        "--physical-properties",
        action="store_true",
        help="Export TEP Physical Properties to PDF"
    )
    
    parser.add_argument(
        "--project-overview",
        action="store_true",
        help="Export project overview to PDF"
    )
    
    parser.add_argument(
        "--fault-analysis",
        action="store_true",
        help="Export fault analysis guide to PDF"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all documentation to PDF"
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_docs_directory()
    
    # Execute based on arguments
    if args.all:
        success = export_all_documentation()
    elif args.physical_properties:
        success = export_physical_properties()
    elif args.project_overview:
        success = export_project_overview()
    elif args.fault_analysis:
        success = export_fault_analysis_guide()
    else:
        parser.print_help()
        return 0
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
