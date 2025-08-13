#!/bin/bash

# TEP Repository Cleanup Script
# Safely removes obsolete hidden folders while preserving essential ones

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

info() {
    echo -e "${BLUE}ℹ️  $*${NC}"
}

success() {
    echo -e "${GREEN}✅ $*${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $*${NC}"
}

error() {
    echo -e "${RED}❌ $*${NC}"
}

# Folders to remove (obsolete/unnecessary)
readonly FOLDERS_TO_REMOVE=(
    ".bmad-core"     # AI development workflow system - not related to TEP
    ".clinerules"    # Code linting rules - obsolete
    ".gemini"        # Google Gemini AI cache - not needed
    ".history"       # IDE history files - already in .gitignore
)

# Folders to keep (essential/useful)
readonly FOLDERS_TO_KEEP=(
    ".git"           # Git repository - essential
    ".augment"       # Augment AI steering files - used by current AI system
    ".vscode"        # VS Code settings - useful for development
)

main() {
    info "🧹 TEP Repository Cleanup - Hidden Folders"
    info "==========================================="
    info ""
    
    cd "$PROJECT_ROOT"
    
    info "Current directory: $(pwd)"
    info ""
    
    # Show current hidden folders
    info "📊 Current hidden folders and their sizes:"
    if command -v du &> /dev/null; then
        for folder in .*/; do
            if [[ -d "$folder" && "$folder" != "./" && "$folder" != "../" ]]; then
                size=$(du -sh "$folder" 2>/dev/null | cut -f1 || echo "N/A")
                echo "   $folder - $size"
            fi
        done
    fi
    info ""
    
    # Show what will be removed
    info "🗑️  Folders scheduled for removal:"
    for folder in "${FOLDERS_TO_REMOVE[@]}"; do
        if [[ -d "$folder" ]]; then
            size=$(du -sh "$folder" 2>/dev/null | cut -f1 || echo "N/A")
            echo "   ❌ $folder ($size) - Obsolete/unnecessary"
        else
            echo "   ⏭️  $folder - Not found (already clean)"
        fi
    done
    info ""
    
    # Show what will be kept
    info "✅ Folders that will be preserved:"
    for folder in "${FOLDERS_TO_KEEP[@]}"; do
        if [[ -d "$folder" ]]; then
            size=$(du -sh "$folder" 2>/dev/null | cut -f1 || echo "N/A")
            echo "   ✅ $folder ($size) - Essential/useful"
        else
            echo "   ⚠️  $folder - Not found"
        fi
    done
    info ""
    
    # Confirmation prompt
    warning "This will permanently delete the obsolete folders listed above."
    warning "Make sure you have committed any important changes to git first."
    info ""
    read -p "Do you want to proceed with cleanup? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Cleanup cancelled by user"
        exit 0
    fi
    
    info ""
    info "🚀 Starting cleanup process..."
    info ""
    
    # Remove obsolete folders
    local removed_count=0
    local total_size_saved=0
    
    for folder in "${FOLDERS_TO_REMOVE[@]}"; do
        if [[ -d "$folder" ]]; then
            info "Removing $folder..."
            
            # Get size before removal (for reporting)
            if command -v du &> /dev/null; then
                size_kb=$(du -sk "$folder" 2>/dev/null | cut -f1 || echo "0")
                total_size_saved=$((total_size_saved + size_kb))
            fi
            
            # Create backup in temp folder (just in case)
            if [[ ! -d "temp/cleanup-backup" ]]; then
                mkdir -p "temp/cleanup-backup"
            fi
            
            info "  Creating backup in temp/cleanup-backup/$folder..."
            cp -r "$folder" "temp/cleanup-backup/" 2>/dev/null || true
            
            # Remove the folder
            rm -rf "$folder"
            
            if [[ ! -d "$folder" ]]; then
                success "  Successfully removed $folder"
                removed_count=$((removed_count + 1))
            else
                error "  Failed to remove $folder"
            fi
        else
            info "Skipping $folder (not found)"
        fi
    done
    
    info ""
    success "🎉 Cleanup completed!"
    success "   Folders removed: $removed_count"
    
    if command -v du &> /dev/null && [[ $total_size_saved -gt 0 ]]; then
        # Convert KB to human readable
        if [[ $total_size_saved -gt 1048576 ]]; then
            size_mb=$((total_size_saved / 1024))
            success "   Space saved: ~${size_mb} MB"
        elif [[ $total_size_saved -gt 1024 ]]; then
            size_mb=$((total_size_saved / 1024))
            success "   Space saved: ~${size_mb} MB"
        else
            success "   Space saved: ~${total_size_saved} KB"
        fi
    fi
    
    info ""
    info "📁 Backups created in temp/cleanup-backup/ (can be removed later)"
    info "🔍 Remaining hidden folders:"
    for folder in .*/; do
        if [[ -d "$folder" && "$folder" != "./" && "$folder" != "../" ]]; then
            size=$(du -sh "$folder" 2>/dev/null | cut -f1 || echo "N/A")
            echo "   ✅ $folder - $size"
        fi
    done
    
    info ""
    success "Repository cleanup complete! 🎉"
    info ""
    info "Next steps:"
    info "1. Test that the TEP integration system still works correctly"
    info "2. Commit the cleanup changes: git add -A && git commit -m 'chore: cleanup obsolete hidden folders'"
    info "3. Remove backup folder when confident: rm -rf temp/cleanup-backup"
}

main "$@"
