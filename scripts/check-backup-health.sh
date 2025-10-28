#!/bin/bash

# Le Grimoire - Backup Health Check Script
# Monitors backup status and alerts if issues are found

set -e

# Helper function for cross-platform file modification time
get_file_mtime() {
    local file="$1"
    if [ -f "$file" ]; then
        # Try GNU stat first (Linux)
        if stat -c %Y "$file" 2>/dev/null; then
            return 0
        # Try BSD stat (macOS)
        elif stat -f %m "$file" 2>/dev/null; then
            return 0
        # Fallback using find
        else
            echo $(( $(date +%s) - 86400 ))  # Fallback: assume 1 day old
        fi
    fi
}

# Helper function for human-readable size
human_readable_size() {
    local size_kb="$1"
    if command -v numfmt >/dev/null 2>&1; then
        numfmt --to=iec-i --suffix=B "$((size_kb * 1024))"
    else
        # Fallback for systems without numfmt (e.g., macOS)
        if [ $size_kb -ge 1048576 ]; then
            echo "$((size_kb / 1048576))GiB"
        elif [ $size_kb -ge 1024 ]; then
            echo "$((size_kb / 1024))MiB"
        else
            echo "${size_kb}KiB"
        fi
    fi
}

echo "========================================"
echo "Le Grimoire - Backup Health Check"
echo "========================================"
echo ""

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
MAX_AGE_HOURS="${MAX_AGE_HOURS:-26}"  # Alert if last backup is older than this
MIN_SIZE_KB="${MIN_SIZE_KB:-100}"     # Alert if backup is smaller than this
WARNING_COUNT=0
ERROR_COUNT=0

# Color codes (optional, work in most terminals)
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Functions
log_ok() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    WARNING_COUNT=$((WARNING_COUNT + 1))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ERROR_COUNT=$((ERROR_COUNT + 1))
}

log_info() {
    echo "ℹ️  $1"
}

# Check if backup directory exists
echo "📁 Checking backup directory..."
if [ ! -d "$BACKUP_DIR" ]; then
    log_error "Backup directory not found: $BACKUP_DIR"
    echo ""
    echo "Please create the backup directory:"
    echo "   mkdir -p $BACKUP_DIR"
    exit 2
fi
log_ok "Backup directory exists: $BACKUP_DIR"

# Check for backup files
echo ""
echo "📊 Checking for backup files..."
BACKUP_FILES=$(find "$BACKUP_DIR" -name "backup_*.tar.gz" -type f 2>/dev/null | wc -l)

if [ "$BACKUP_FILES" -eq 0 ]; then
    log_error "No backup files found in $BACKUP_DIR"
    echo ""
    echo "Create your first backup:"
    echo "   ./scripts/backup-production.sh"
    exit 2
fi

log_ok "Found $BACKUP_FILES backup file(s)"

# Find latest backup
echo ""
echo "🔍 Analyzing latest backup..."
LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    log_error "Could not identify latest backup"
    exit 2
fi

BACKUP_NAME=$(basename "$LATEST_BACKUP")
log_info "Latest backup: $BACKUP_NAME"

# Check backup age
BACKUP_TIMESTAMP=$(get_file_mtime "$LATEST_BACKUP")
BACKUP_AGE_SECONDS=$(( $(date +%s) - BACKUP_TIMESTAMP ))
BACKUP_AGE_HOURS=$(( BACKUP_AGE_SECONDS / 3600 ))
BACKUP_AGE_MINUTES=$(( (BACKUP_AGE_SECONDS % 3600) / 60 ))

if [ $BACKUP_AGE_HOURS -gt $MAX_AGE_HOURS ]; then
    log_error "Latest backup is too old: ${BACKUP_AGE_HOURS}h ${BACKUP_AGE_MINUTES}m"
    echo "         Expected: < ${MAX_AGE_HOURS} hours"
else
    log_ok "Backup age is acceptable: ${BACKUP_AGE_HOURS}h ${BACKUP_AGE_MINUTES}m"
fi

# Check backup size
BACKUP_SIZE_KB=$(du -k "$LATEST_BACKUP" | cut -f1)
BACKUP_SIZE_HUMAN=$(du -h "$LATEST_BACKUP" | cut -f1)

if [ $BACKUP_SIZE_KB -lt $MIN_SIZE_KB ]; then
    log_warning "Backup size is suspiciously small: $BACKUP_SIZE_HUMAN"
    echo "           Expected: > ${MIN_SIZE_KB}KB"
else
    log_ok "Backup size is acceptable: $BACKUP_SIZE_HUMAN"
fi

# Check backup integrity
echo ""
echo "🔍 Checking backup integrity..."
if tar -tzf "$LATEST_BACKUP" > /dev/null 2>&1; then
    log_ok "Backup archive is valid"
    
    # Count files in archive
    FILE_COUNT=$(tar -tzf "$LATEST_BACKUP" | wc -l)
    log_info "Archive contains $FILE_COUNT files/directories"
    
    # Check for expected files
    MISSING_FILES=()
    
    if ! tar -tzf "$LATEST_BACKUP" | grep -q "backup_info.txt"; then
        MISSING_FILES+=("backup_info.txt")
    fi
    
    if ! tar -tzf "$LATEST_BACKUP" | grep -q "mongodb/"; then
        MISSING_FILES+=("mongodb/")
    fi
    
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        log_warning "Missing expected files/directories:"
        for file in "${MISSING_FILES[@]}"; do
            echo "           - $file"
        done
    else
        log_ok "All expected components present"
    fi
else
    log_error "Backup archive is corrupted or invalid"
fi

# Check disk space
echo ""
echo "💾 Checking disk space..."
BACKUP_PARTITION=$(df "$BACKUP_DIR" | tail -1)
DISK_USAGE=$(echo "$BACKUP_PARTITION" | awk '{print $5}' | sed 's/%//')
DISK_AVAILABLE=$(echo "$BACKUP_PARTITION" | awk '{print $4}')
DISK_AVAILABLE_HUMAN=$(human_readable_size "$DISK_AVAILABLE")

if [ $DISK_USAGE -gt 90 ]; then
    log_error "Disk usage is critical: ${DISK_USAGE}%"
    echo "          Available: $DISK_AVAILABLE_HUMAN"
elif [ $DISK_USAGE -gt 80 ]; then
    log_warning "Disk usage is high: ${DISK_USAGE}%"
    echo "            Available: $DISK_AVAILABLE_HUMAN"
else
    log_ok "Disk usage is acceptable: ${DISK_USAGE}%"
    log_info "Available space: $DISK_AVAILABLE_HUMAN"
fi

# List all backups
echo ""
echo "📋 Backup inventory:"
echo "    Total backups: $BACKUP_FILES"
echo ""

ls -lht "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | head -5 | while read line; do
    SIZE=$(echo "$line" | awk '{print $5}')
    DATE=$(echo "$line" | awk '{print $6, $7, $8}')
    NAME=$(echo "$line" | awk '{print $9}')
    BASE_NAME=$(basename "$NAME")
    echo "    - $BASE_NAME ($SIZE) - $DATE"
done

if [ $BACKUP_FILES -gt 5 ]; then
    echo "    ... and $((BACKUP_FILES - 5)) more"
fi

# Calculate total backup size
echo ""
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
log_info "Total backup storage: $TOTAL_SIZE"

# Summary
echo ""
echo "========================================"
echo "Summary"
echo "========================================"
echo ""

if [ $ERROR_COUNT -eq 0 ] && [ $WARNING_COUNT -eq 0 ]; then
    log_ok "All checks passed!"
    echo ""
    echo "Backup Status: HEALTHY"
    EXIT_CODE=0
elif [ $ERROR_COUNT -eq 0 ]; then
    echo "Status: OK with $WARNING_COUNT warning(s)"
    echo ""
    echo "Backup Status: WARNING"
    EXIT_CODE=0
else
    echo "Status: $ERROR_COUNT error(s), $WARNING_COUNT warning(s)"
    echo ""
    echo "Backup Status: CRITICAL"
    EXIT_CODE=1
fi

echo ""
echo "Recommendations:"
if [ $BACKUP_AGE_HOURS -gt $MAX_AGE_HOURS ]; then
    echo "  • Run a new backup immediately:"
    echo "    ./scripts/backup-production.sh"
fi

if [ $DISK_USAGE -gt 80 ]; then
    echo "  • Free up disk space or adjust retention:"
    echo "    BACKUP_RETENTION_DAYS=3 ./scripts/backup-production.sh"
fi

if [ $ERROR_COUNT -gt 0 ] || [ $WARNING_COUNT -gt 0 ]; then
    echo "  • Review backup procedures:"
    echo "    docs/operations/BACKUP_RESTORE.md"
fi

echo ""

exit $EXIT_CODE
