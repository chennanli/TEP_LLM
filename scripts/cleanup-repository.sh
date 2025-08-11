#!/bin/bash

# TEP Repository Cleanup Script
# Moves unnecessary files to temp folder for later review/deletion

set -e

echo "🧹 TEP Repository Cleanup"
echo "========================"

# Create temp directory for files to review
mkdir -p temp/review-for-deletion
mkdir -p temp/review-for-deletion/backup-files
mkdir -p temp/review-for-deletion/generated-pdfs
mkdir -p temp/review-for-deletion/test-files
mkdir -p temp/review-for-deletion/setup-scripts
mkdir -p temp/review-for-deletion/generated-data
mkdir -p temp/review-for-deletion/redundant-folders

echo "📁 Created temp directories for review..."

# Move backup/redundant Python files
echo "🗑️ Moving backup and redundant files..."
backup_files=(
    "unified_tep_control_panel.py.bak"
    "unified_tep_control_panel_backup_20250810_030216.py"
    "unified_tep_control_panel_debug.py"
    "unified_control_panel_clean.py"
    "unified_tep_control_panel_clean_v2.py"
    "working_tep_dashboard.py"
)

for file in "${backup_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Moving $file"
        mv "$file" temp/review-for-deletion/backup-files/
    fi
done

# Move generated PDFs
echo "📄 Moving generated PDF files..."
pdf_files=(
    "TEP_Component_Validation_Final_Report.pdf"
    "TEP_Component_Validation_Report.pdf"
    "TEP_Fault_Analysis_GroundTruth_Validation.pdf"
    "TEP_Physical_Properties.pdf"
    "TEP_Reactions_Final_Assessment.pdf"
)

for file in "${pdf_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Moving $file"
        mv "$file" temp/review-for-deletion/generated-pdfs/
    fi
done

# Move test files
echo "🧪 Moving test and temporary files..."
test_files=(
    "test_buttons.html"
    "test_ingest.json"
    "simple_button_test.py"
    "simple_start.py"
    "simple_tep_test.py"
    "test_all_simulators.py"
    "external_js_test_panel.py"
    "control_panel_js.js"
)

for file in "${test_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Moving $file"
        mv "$file" temp/review-for-deletion/test-files/
    fi
done

# Move setup/export scripts
echo "🔧 Moving one-time setup and export scripts..."
setup_files=(
    "export_fault_groundtruth_pdf.py"
    "export_final_validation_pdf.py"
    "export_reactions_pdf.py"
    "export_to_pdf.py"
    "export_validation_pdf.py"
    "generate_training_data.py"
    "setup_faultexplainer.sh"
    "setup_git_repo.sh"
    "push_to_github.sh"
    "reset_and_recommit.sh"
    "clean_repo.sh"
    "start_all.sh"
    "start_faultexplainer.sh"
    "start_tep_bridge.sh"
)

for file in "${setup_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Moving $file"
        mv "$file" temp/review-for-deletion/setup-scripts/
    fi
done

# Move generated data files
echo "📊 Moving generated data files..."
data_files=(
    "tep_simulation_fault_0_4h.csv"
    "tep_simulation_fault_1_6h.csv"
    "backend.out"
)

for file in "${data_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  Moving $file"
        mv "$file" temp/review-for-deletion/generated-data/
    fi
done

# Move redundant folders
echo "🗂️ Moving redundant folders..."
if [ -d "src" ] && [ -d "integration/src" ]; then
    echo "  Moving redundant src/ folder (exists in integration/)"
    mv src temp/review-for-deletion/redundant-folders/
fi

if [ -d "__pycache__" ]; then
    echo "  Moving __pycache__/ folder"
    mv __pycache__ temp/review-for-deletion/redundant-folders/
fi

# Clean up docs folder (move redundant documentation)
echo "📚 Cleaning up docs folder..."
mkdir -p temp/review-for-deletion/redundant-docs

redundant_docs=(
    "docs/API_UPDATE_SUMMARY.md"
    "docs/COMMIT_SUMMARY.md"
    "docs/DOCUMENTATION_CLEANUP_SUMMARY.md"
    "docs/MVP_IMPLEMENTATION_PLAN.md"
    "docs/SAFARI_JAVASCRIPT_FIX_SUMMARY.md"
    "docs/conversation_history.md"
    "docs/conversation_history_compressed.md"
    "docs/expert_handoff_prompt.md"
    "docs/find_llm_explanations.md"
    "docs/get_llm_explanations.md"
    "docs/reactions_guess.md"
)

for file in "${redundant_docs[@]}"; do
    if [ -f "$file" ]; then
        echo "  Moving $file"
        mv "$file" temp/review-for-deletion/redundant-docs/
    fi
done

# Create summary of what was moved
echo "📝 Creating cleanup summary..."
cat > temp/CLEANUP_SUMMARY.md << 'EOF'
# Repository Cleanup Summary

## 🗑️ Files Moved to temp/review-for-deletion/

### backup-files/
- Old backup versions of Python files
- Debug versions and clean versions
- Can be safely deleted

### generated-pdfs/
- PDF reports that can be regenerated
- Export scripts can recreate these
- Can be safely deleted

### test-files/
- Temporary test files and HTML tests
- One-off testing scripts
- Can be safely deleted

### setup-scripts/
- One-time setup and export scripts
- Git management scripts
- Can be safely deleted after confirming not needed

### generated-data/
- CSV simulation results
- Log files and outputs
- Can be safely deleted (data can be regenerated)

### redundant-folders/
- Duplicate src/ folder
- Python cache files
- Can be safely deleted

### redundant-docs/
- Conversation histories
- Temporary documentation
- Implementation summaries
- Can be safely deleted

## ✅ Files Kept in Repository

### Essential Files:
- README.md
- LICENSE
- requirements.txt
- .gitignore

### Core Folders:
- integration/ - Production system
- legacy/ - Working system
- docs/ - Essential documentation (cleaned)
- scripts/ - Utility scripts
- tep_env/ - Virtual environment

## 🎯 Next Steps

1. Review files in temp/review-for-deletion/
2. Confirm you don't need any of them
3. Delete temp/ folder entirely
4. Commit clean repository

## 🚨 Safety Note

All files are moved to temp/, not deleted. You can restore any file if needed.
EOF

echo ""
echo "✅ Repository cleanup complete!"
echo ""
echo "📊 Summary:"
echo "  • Moved $(find temp/review-for-deletion -type f | wc -l) files to temp/ for review"
echo "  • Kept essential files and core folders"
echo "  • Created cleanup summary in temp/CLEANUP_SUMMARY.md"
echo ""
echo "🎯 Next steps:"
echo "  1. Review temp/CLEANUP_SUMMARY.md"
echo "  2. Check temp/review-for-deletion/ folders"
echo "  3. If satisfied, delete temp/ folder entirely"
echo "  4. Commit the clean repository"
echo ""
echo "🚨 Safety: All files moved to temp/, not deleted!"
