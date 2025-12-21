# Backup and Recovery Guide (GAP-58)

This guide covers automated backup and disaster recovery procedures for the Solarpunk DTN Bundle System.

## Overview

The backup system provides:
- **Automated SQLite backups** using hot backup method (safe while app is running)
- **Integrity verification** of all backups
- **Compression** to save storage space
- **Optional S3 upload** for off-site backup
- **Retention policy** (7 days by default)
- **Safe restore** with automatic safety backups

## Backup Script

### Basic Usage

```bash
# Use default locations (./dtn_bundles.db -> ./backups/)
./scripts/backup.sh

# Specify custom database and backup directory
./scripts/backup.sh /path/to/database.db /path/to/backups
```

### Environment Variables

```bash
# Database location (default: ./dtn_bundles.db)
export DATABASE_PATH="/custom/path/dtn_bundles.db"

# Backup storage directory (default: ./backups)
export BACKUP_DIR="/backups"

# Retention policy in days (default: 7)
export BACKUP_RETENTION_DAYS=14

# S3 bucket for remote backup (optional)
export BACKUP_S3_BUCKET="my-backup-bucket"
export BACKUP_S3_PATH="solarpunk/backups/"
```

### Automated Backups with Cron

1. Copy the example cron file:
   ```bash
   cp scripts/backup.cron.example scripts/backup.cron
   ```

2. Edit with your paths:
   ```bash
   nano scripts/backup.cron
   ```

3. Install the cron job:
   ```bash
   crontab -e
   # Paste the schedule from backup.cron
   ```

4. Verify it's installed:
   ```bash
   crontab -l
   ```

5. Monitor backup logs:
   ```bash
   tail -f /var/log/dtn-backup.log
   ```

### Backup Output

Successful backups produce:
- Compressed backup file: `backups/dtn_backup_YYYYMMDD_HHMMSS.db.gz`
- JSON output for monitoring:
  ```json
  {
    "timestamp": "2025-12-20T12:00:00Z",
    "backup_file": "dtn_backup_20251220_120000.db.gz",
    "backup_size": "42M",
    "database": "./dtn_bundles.db",
    "status": "success"
  }
  ```

## Restore Script

### Basic Usage

```bash
# Restore from compressed backup
./scripts/restore.sh backups/dtn_backup_20251220_120000.db.gz

# Restore from uncompressed backup
./scripts/restore.sh backups/dtn_backup_20251220_120000.db

# Specify custom database path
./scripts/restore.sh backups/dtn_backup_20251220_120000.db.gz /path/to/database.db
```

### Restore with Service Management

```bash
# Stop service before restore, restart after
RESTORE_STOP_SERVICE=true SERVICE_NAME=dtn-bundle-system ./scripts/restore.sh backup.db.gz
```

### Safety Features

The restore script:
1. **Verifies backup integrity** before starting
2. **Creates safety backup** of current database to `./backups/pre-restore/`
3. **Verifies restored database** after restore
4. **Rolls back to safety backup** if restore fails

### Restore Output

Successful restore produces:
- Restored database at specified path
- Safety backup at `./backups/pre-restore/pre_restore_YYYYMMDD_HHMMSS.db`
- JSON output:
  ```json
  {
    "timestamp": "2025-12-20T12:30:00Z",
    "backup_file": "backups/dtn_backup_20251220_120000.db.gz",
    "database": "./dtn_bundles.db",
    "db_size": "42M",
    "table_count": 15,
    "status": "success"
  }
  ```

## Disaster Recovery Procedures

### Scenario 1: Database Corruption

1. Stop the application:
   ```bash
   sudo systemctl stop dtn-bundle-system
   ```

2. Find the latest backup:
   ```bash
   ls -lht backups/ | head -5
   ```

3. Restore from backup:
   ```bash
   ./scripts/restore.sh backups/dtn_backup_YYYYMMDD_HHMMSS.db.gz
   ```

4. Verify integrity:
   ```bash
   sqlite3 ./dtn_bundles.db "PRAGMA integrity_check"
   ```

5. Start the application:
   ```bash
   sudo systemctl start dtn-bundle-system
   ```

### Scenario 2: Accidental Data Loss

1. Find backup from before data loss:
   ```bash
   ls -l backups/
   # Look for timestamp before data was lost
   ```

2. Restore (with automatic safety backup):
   ```bash
   RESTORE_STOP_SERVICE=true ./scripts/restore.sh backups/dtn_backup_YYYYMMDD_HHMMSS.db.gz
   ```

3. Verify data is restored:
   ```bash
   sqlite3 ./dtn_bundles.db "SELECT COUNT(*) FROM bundles"
   ```

### Scenario 3: Complete System Failure

1. Set up new system
2. Install dependencies
3. Restore latest backup:
   ```bash
   # If backup in S3
   aws s3 cp s3://my-bucket/backups/dtn_backup_latest.db.gz ./
   ./scripts/restore.sh dtn_backup_latest.db.gz
   ```

4. Start application:
   ```bash
   sudo systemctl start dtn-bundle-system
   ```

## Monitoring

### Check Backup Status

```bash
# List backups
ls -lht backups/

# Count backups
find backups/ -name "dtn_backup_*.db.gz" | wc -l

# Total backup size
du -sh backups/

# Parse latest backup JSON output
tail -1 /var/log/dtn-backup.log | jq .
```

### Set Up Alerts

Monitor `/var/log/dtn-backup.log` for failures:

```bash
# Check for failed backups in last 24 hours
grep -A 5 'ERROR' /var/log/dtn-backup.log | tail -20

# Set up logwatch or similar monitoring
# Alert if no successful backup in 25 hours
```

## S3 Backup Configuration

### AWS CLI Setup

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# Enter your AWS access key, secret key, and region
```

### S3 Bucket Setup

```bash
# Create bucket
aws s3 mb s3://my-solarpunk-backups

# Set lifecycle policy (optional - keep backups for 30 days)
cat > lifecycle.json <<EOF
{
  "Rules": [
    {
      "Id": "DeleteOldBackups",
      "Status": "Enabled",
      "Prefix": "backups/",
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket my-solarpunk-backups \
  --lifecycle-configuration file://lifecycle.json
```

### Enable S3 Backups

```bash
# Set environment variable
export BACKUP_S3_BUCKET="my-solarpunk-backups"
export BACKUP_S3_PATH="solarpunk/production/"

# Run backup (will upload to S3)
./scripts/backup.sh
```

## Testing

### Test Backup

```bash
# Create test database
sqlite3 test.db "CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)"
sqlite3 test.db "INSERT INTO test (value) VALUES ('test data')"

# Backup
DATABASE_PATH=test.db BACKUP_DIR=./test-backups ./scripts/backup.sh

# Verify backup exists and is compressed
ls -lh test-backups/
```

### Test Restore

```bash
# Corrupt database
echo "corrupted" > test.db

# Restore from backup
./scripts/restore.sh test-backups/dtn_backup_*.db.gz test.db

# Verify data
sqlite3 test.db "SELECT * FROM test"
# Should show: 1|test data

# Cleanup
rm -rf test.db test-backups/
```

## Best Practices

1. **Test restores regularly** - At least monthly, restore a backup to verify it works
2. **Monitor backup logs** - Set up alerts for backup failures
3. **Use S3 for production** - Keep off-site backups in case of hardware failure
4. **Keep multiple backup versions** - Don't rely on just the latest backup
5. **Document your schedule** - Know when backups run and how long they're kept
6. **Secure backups** - Backups contain sensitive data, encrypt if storing remotely
7. **Test disaster recovery** - Practice full system recovery in a test environment

## Troubleshooting

### Backup fails with "database is locked"

The backup script uses SQLite's `.backup` command which handles locks safely. If you still see this:
- Check for other processes accessing the database
- Ensure the app is running normally (not crashed/hung)

### Restore fails with integrity check error

The backup is corrupted:
- Try an earlier backup
- Check disk space and filesystem health
- Verify S3 download completed if restoring from remote

### Out of disk space

Adjust retention policy:
```bash
export BACKUP_RETENTION_DAYS=3
./scripts/backup.sh
```

Or manually clean old backups:
```bash
find backups/ -name "dtn_backup_*.db.gz" -mtime +3 -delete
```

## Files

- `scripts/backup.sh` - Automated backup script
- `scripts/restore.sh` - Database restore script
- `scripts/backup.cron.example` - Example cron schedule
- `scripts/BACKUP_RECOVERY.md` - This documentation
