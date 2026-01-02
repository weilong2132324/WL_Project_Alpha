#!/bin/bash

# 1. Configuration & Setup
# ------------------------
# Define constants (or read them from your .env file)
CONTAINER_NAME="wl_project_alpha-db-1"  # Check 'docker ps' for exact name
DB_USER="root"
DB_PASS="secret"       # Ideally, source this from .env
DB_NAME="alpha_db"
BACKUP_FILE="pre_migration_backup.sql"

# Colors for pretty output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[Step 1] Creating Safety Net Backup...${NC}"

# 2. The Backup (Dump)
# --------------------
# We use 'docker exec' to run mysqldump INSIDE the container, 
# but we redirect (>) the output to a file on your HOST machine.
docker exec "$CONTAINER_NAME" mysqldump -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$BACKUP_FILE"

# Check if the backup actually worked
if [ $? -ne 0 ]; then
    echo -e "${RED}Critical Error: Backup failed. Aborting migration to ensure safety.${NC}"
    rm -f "$BACKUP_FILE"
    exit 1
fi

echo -e "${GREEN}Backup saved to $BACKUP_FILE.${NC}"
echo -e "${YELLOW}[Step 2] Applying Go Migrations...${NC}"

# 3. The Risky Operation
# ----------------------
# Run your Go migration command. 
# NOTE: Replace this with your actual command (e.g., ./app migrate)
go run main.go migrate

# Capture the exit code of the migration command immediately
MIGRATION_STATUS=$?

# 4. The Decision Logic
# ---------------------
if [ $MIGRATION_STATUS -eq 0 ]; then
    # --- SUCCESS PATH ---
    echo -e "${GREEN}Migrations applied successfully!${NC}"
    echo "Cleaning up backup file..."
    rm -f "$BACKUP_FILE"
    echo -e "${GREEN}Deployment Complete.${NC}"
    exit 0
else
    # --- FAILURE PATH (Rollback) ---
    echo -e "${RED}!!! MIGRATION FAILED (Exit Code: $MIGRATION_STATUS) !!!${NC}"
    echo -e "${YELLOW}Initiating Automatic Rollback...${NC}"
    
    # Restore the database from the backup file
    # We use '<' to pipe the file on your HOST into the mysql command INSIDE the container
    cat "$BACKUP_FILE" | docker exec -i "$CONTAINER_NAME" mysql -u"$DB_USER" -p"$DB_PASS" "$DB_NAME"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Rollback successful. Database restored to pre-flight state.${NC}"
        echo "Check your migration logs to debug the error."
        rm -f "$BACKUP_FILE"
    else
        echo -e "${RED}CRITICAL: Rollback failed! Database may be in inconsistent state.${NC}"
        # Keep the backup file so you can manually restore later
    fi
    
    exit 1
fi
