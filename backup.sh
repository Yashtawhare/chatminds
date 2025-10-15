#!/bin/bash

# Backup Script for ChatMinds
# Creates backups of database, uploaded files, and configuration

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "📦 Creating ChatMinds backup..."
echo "Backup directory: $BACKUP_DIR"

# Backup database
echo "💾 Backing up database..."
if docker-compose ps | grep -q "chatminds-web.*Up"; then
    docker-compose exec -T chatminds-web cat /app/askai.db > "$BACKUP_DIR/askai.db"
    echo "✅ Database backed up"
else
    echo "❌ ChatMinds web service not running"
fi

# Backup uploaded documents and data
echo "📁 Backing up data directories..."
if [ -d "chatminds/data" ]; then
    cp -r chatminds/data "$BACKUP_DIR/chatminds_data"
    echo "✅ ChatMinds data backed up"
fi

if [ -d "chatminds-llm/data" ]; then
    cp -r chatminds-llm/data "$BACKUP_DIR/llm_data"
    echo "✅ LLM data backed up"
fi

# Backup configuration files
echo "⚙️ Backing up configuration..."
cp .env "$BACKUP_DIR/.env.backup" 2>/dev/null || echo "⚠️  .env file not found"
cp docker-compose.yml "$BACKUP_DIR/"
cp -r nginx "$BACKUP_DIR/"

# Create backup info file
cat > "$BACKUP_DIR/backup_info.txt" << EOF
ChatMinds Backup Information
===========================
Backup Date: $(date)
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "Not available")
Git Branch: $(git branch --show-current 2>/dev/null || echo "Not available")

Services Status at Backup Time:
$(docker-compose ps 2>/dev/null || echo "Docker not available")

System Info:
- Hostname: $(hostname)
- OS: $(uname -a)
- Disk Usage: $(df -h . | tail -1)
- Memory: $(free -h | grep Mem)
EOF

# Create compressed archive
echo "🗜️ Creating compressed archive..."
tar -czf "backup_$(date +%Y%m%d_%H%M%S).tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "✅ Backup completed successfully!"
echo "📁 Backup file: backup_$(date +%Y%m%d_%H%M%S).tar.gz"

# Clean up old backups (keep last 7)
echo "🧹 Cleaning up old backups (keeping last 7)..."
ls -t backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true

echo ""
echo "📋 Backup Summary:"
ls -lh backup_*.tar.gz 2>/dev/null | tail -5 || echo "No backup files found"