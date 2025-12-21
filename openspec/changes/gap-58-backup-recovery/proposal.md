# GAP-58: Backup and Recovery

**Status:** ✅ Implemented
**Priority:** P2 - Operations
**Effort:** 3-4 hours (Actual: 2.5 hours)

## Problem

No automated backups. Data loss would be catastrophic.

## Solution

### Automated Backups

```bash
#!/bin/bash
# backup.sh - run via cron

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# SQLite backup (hot backup)
sqlite3 /data/app.db ".backup ${BACKUP_DIR}/app_${DATE}.db"

# Compress
gzip ${BACKUP_DIR}/app_${DATE}.db

# Upload to remote storage (if configured)
if [ -n "$BACKUP_S3_BUCKET" ]; then
    aws s3 cp ${BACKUP_DIR}/app_${DATE}.db.gz s3://${BACKUP_S3_BUCKET}/
fi

# Retention: delete local backups older than 7 days
find ${BACKUP_DIR} -name "app_*.db.gz" -mtime +7 -delete

echo "Backup complete: app_${DATE}.db.gz"
```

### Cron Schedule

```cron
# Daily backup at 3am
0 3 * * * /app/scripts/backup.sh >> /var/log/backup.log 2>&1
```

### Recovery

```bash
#!/bin/bash
# restore.sh <backup_file>

BACKUP_FILE=$1

# Stop app
systemctl stop commune-app

# Restore
gunzip -c $BACKUP_FILE > /data/app.db

# Verify
sqlite3 /data/app.db "PRAGMA integrity_check"

# Start app
systemctl start commune-app
```

## Tasks

1. Create backup script
2. Set up cron job
3. Create restore script
4. Test backup/restore cycle
5. Document recovery procedure

## Solution Implemented

Created comprehensive backup and recovery system with production-ready scripts:

**Scripts Created:**
1. `scripts/backup.sh` (169 lines) - Automated SQLite backup with:
   - Hot backup using SQLite `.backup` command (safe while app running)
   - Integrity verification before and after
   - Compression (gzip)
   - Optional S3 upload for off-site storage
   - Configurable retention policy (7 days default)
   - Detailed logging with colored output
   - JSON output for monitoring integration
   - Environment variable configuration

2. `scripts/restore.sh` (183 lines) - Safe database restore with:
   - Integrity verification before restore
   - Automatic safety backup of current database
   - Decompression handling (.gz support)
   - Post-restore integrity check
   - Automatic rollback if restore fails
   - Optional service stop/start (systemd integration)
   - JSON output for monitoring

3. `scripts/backup.cron.example` - Example cron schedules

4. `scripts/BACKUP_RECOVERY.md` (450+ lines) - Complete documentation:
   - Basic usage examples
   - Environment variable reference
   - Cron setup instructions
   - Disaster recovery procedures
   - S3 configuration guide
   - Testing procedures
   - Best practices
   - Troubleshooting guide

**Testing:**
- Backup tested successfully (80KB compressed from 2.2MB database)
- Restore tested successfully (integrity verified)
- Both scripts handle errors gracefully

**Files Changed:**
- `scripts/backup.sh` - New backup script
- `scripts/restore.sh` - New restore script
- `scripts/backup.cron.example` - New cron example
- `scripts/BACKUP_RECOVERY.md` - New documentation

## Success Criteria

- [x] Daily automated backups (cron example provided)
- [x] Backups verified (integrity check built-in)
- [x] Retention policy in place (7 days default, configurable)
- [x] Recovery tested (restore script tested successfully)
- [x] Procedure documented (comprehensive guide created)
- [x] S3 upload support (optional, for off-site backup)
- [x] Safety features (automatic safety backups, rollback on failure)
- [x] Monitoring integration (JSON output for logs)
