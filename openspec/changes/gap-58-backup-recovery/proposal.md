# GAP-58: Backup and Recovery

**Status:** Draft
**Priority:** P2 - Operations
**Effort:** 3-4 hours

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

## Success Criteria

- [ ] Daily automated backups
- [ ] Backups verified (integrity check)
- [ ] Retention policy in place
- [ ] Recovery tested
- [ ] Procedure documented
