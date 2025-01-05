#!/bin/bash

# Variables
DUMP_FILE=$1              # Path to the SQL dump file
CONTAINER_NAME="cgdac_postgres"  # Default container name
ENV_FILE="../.env"           # Path to the .env file

# Check if the dump file argument is provided
if [[ -z "$DUMP_FILE" ]]; then
  echo "Usage: $0 <dump_file>"
  exit 1
fi

# Check if the dump file exists
if [[ ! -f "$DUMP_FILE" ]]; then
  echo "Error: Dump file '$DUMP_FILE' not found."
  exit 1
fi

# Check if the .env file exists
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env file not found at '$ENV_FILE'."
  exit 1
fi

# Load variables from the .env file
DB_NAME=$(grep -E '^POSTGRES_DATABASE=' "$ENV_FILE" | cut -d '=' -f2)
DB_USER=$(grep -E '^POSTGRES_USER=' "$ENV_FILE" | cut -d '=' -f2)

# Check if DB_NAME and DB_USER were found
if [[ -z "$DB_NAME" || -z "$DB_USER" ]]; then
  echo "Error: DB_NAME or DB_USER not found in .env file."
  exit 1
fi

# Copy the dump file into the container
echo "Copying $DUMP_FILE into container $CONTAINER_NAME..."
docker cp "$DUMP_FILE" "$CONTAINER_NAME:/tmp/db_dump.sql"
if [[ $? -ne 0 ]]; then
  echo "Error: Failed to copy the dump file into the container."
  exit 1
fi

# Restore the database
echo "Restoring the database $DB_NAME..."
docker exec -i "$CONTAINER_NAME" psql -U "$DB_USER" -d "$DB_NAME" -f /tmp/db_dump.sql
if [[ $? -ne 0 ]]; then
  echo "Error: Database restore failed."
  exit 1
fi

# Cleanup
echo "Removing temporary dump file from the container..."
docker exec -i "$CONTAINER_NAME" rm /tmp/db_dump.sql

echo "Database $DB_NAME restored successfully from $DUMP_FILE."